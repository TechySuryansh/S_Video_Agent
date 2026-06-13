# pyrefly: ignore [missing-import]
import os
from sarvam import SarvamAI

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v3")


def transcribe_chunk_sarvam(chunk_path: str, language: str = "english") -> str:
    """Use Sarvam AI for transcription (supports both English and Hinglish)."""
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

    try:
        print(f"  → Transcribing with Sarvam AI...")
        
        # Use Sarvam AI SDK - it handles both English and Hinglish
        response = client.speech_to_text.transcribe(
            file=open(chunk_path, "rb"),
            model=SARVAM_STT_MODEL,
            mode="transcribe"
        )
        
        # Extract transcript from response
        if hasattr(response, 'transcript'):
            return response.transcript
        else:
            return str(response)
                
    except Exception as e:
        print(f"  ❌ Sarvam error: {e}")
        raise


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Transcribe audio chunk using Sarvam AI.
    Supports both English and Hinglish.
    """
    return transcribe_chunk_sarvam(chunk_path, language)


def transcribe_all(chunks: list, language: str = "english") -> str:

    full_transcript = "" 

    print(f"Using Sarvam AI for {language.capitalize()} transcription.")

    for i, chunk in enumerate(chunks):

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language=language)

        full_transcript += text + " "

        try:
            os.remove(chunk)
        except Exception:
            pass

    return full_transcript.strip()  

    
    