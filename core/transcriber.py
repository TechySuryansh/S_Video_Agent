import whisper
import os
import requests

# Try importing pydub with fallback handling for deployment issues
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ pydub import failed: {e}")
    print("🔄 Falling back to ffmpeg-only audio processing")
    PYDUB_AVAILABLE = False
    AudioSegment = None

import subprocess

# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
SARVAM_PIECE_SECONDS = 25


WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")


SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

_model = None


def load_model():

    global _model  

    if _model is None: 
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL) 
        print("Whisper model loaded.")
    return _model 


def transcribe_chunk_whisper(chunk_path: str) -> str:

    model = load_model()  

    result = model.transcribe(chunk_path, task="transcribe")  
    return result["text"]  


def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript."""
    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


def _split_audio_with_ffmpeg(chunk_path: str) -> list:
    """Fallback audio splitting using ffmpeg when pydub is not available."""
    try:
        # Get audio duration using ffprobe
        result = subprocess.run([
            "ffprobe", "-v", "error", 
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            chunk_path
        ], capture_output=True, text=True, check=True)
        
        duration_seconds = float(result.stdout.strip())
        piece_seconds = SARVAM_PIECE_SECONDS
        
        pieces = []
        total_pieces = int((duration_seconds + piece_seconds - 1) / piece_seconds)
        
        for i in range(total_pieces):
            start_time = i * piece_seconds
            piece_path = f"{chunk_path}_sv_{i}.wav"
            
            subprocess.run([
                "ffmpeg", "-i", chunk_path,
                "-ss", str(start_time),
                "-t", str(piece_seconds),
                "-c", "copy", "-y",
                piece_path
            ], check=True, capture_output=True)
            
            pieces.append(piece_path)
        
        return pieces
        
    except Exception as e:
        print(f"❌ ffmpeg splitting failed: {e}")
        return [chunk_path]  # Return original file as fallback


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    full_text = ""
    
    if PYDUB_AVAILABLE:
        # Use pydub for audio processing (preferred)
        audio = AudioSegment.from_wav(chunk_path)
        piece_ms = SARVAM_PIECE_SECONDS * 1000
        total_pieces = (len(audio) + piece_ms - 1) // piece_ms

        for i, start in enumerate(range(0, len(audio), piece_ms)):
            piece = audio[start: start + piece_ms]
            piece_path = f"{chunk_path}_sv_{i}.wav"
            piece.export(piece_path, format="wav")

            try:
                print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
                full_text += _send_to_sarvam(piece_path) + " "
            finally:
                if os.path.exists(piece_path):
                    os.remove(piece_path)
    else:
        # Fallback to ffmpeg for audio processing
        print("🔄 Using ffmpeg fallback for audio splitting")
        pieces = _split_audio_with_ffmpeg(chunk_path)
        
        try:
            for i, piece_path in enumerate(pieces):
                print(f"  → Sarvam piece {i + 1}/{len(pieces)} ...")
                full_text += _send_to_sarvam(piece_path) + " "
        finally:
            # Clean up temporary pieces
            for piece_path in pieces:
                if piece_path != chunk_path and os.path.exists(piece_path):
                    os.remove(piece_path)

    return full_text.strip()

   



def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Whisper or Sarvam depending on language choice.
    - english  → Whisper (local model)
    - hinglish → Sarvam (translates to English while transcribing)
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(chunks: list, language: str = "english") -> str:

    full_transcript = "" 

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):  

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language=language)  

        full_transcript += text + " "  

    print("Transcription complete.")

    return full_transcript.strip()  