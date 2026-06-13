# pyrefly: ignore [missing-import]
import whisper
import os
from sarvam import SarvamAI
# pyrefly: ignore [missing-import]
from pydub import AudioSegment


SARVAM_PIECE_SECONDS = 25 
WHISPER_MODEL=os.getenv("WHISPER_MODEL", "base")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v3")

_model=None


def load_model():

    global _model  

    if _model is None: 
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL) 
        print("Whisper model loaded.")
    return _model 

def transcribe_chunk_whisper(chunk_path: str) -> str:

    model = load_model()  

    result = model.transcribe(chunk_path, task="transcribe", fp16=False, language="en")  
    return result["text"]  



def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Use Sarvam AI native SDK for Hindi/Hinglish transcription.
    Splits large chunks into 25-second pieces, sends each separately, and joins transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            
            # Use Sarvam AI SDK directly
            response = client.speech_to_text.transcribe(
                file=open(piece_path, "rb"),
                model=SARVAM_STT_MODEL,
                mode="transcribe"
            )
            
            # Extract transcript from response
            if hasattr(response, 'transcript'):
                full_text += response.transcript + " "
            else:
                full_text += str(response) + " "
                
        except Exception as e:
            print(f"  ❌ Sarvam error on piece {i+1}: {e}")
            raise
        finally:
            if os.path.exists(piece_path):
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

        try:
            os.remove(chunk)
        except Exception:
            pass

    return full_transcript.strip()  

    
    