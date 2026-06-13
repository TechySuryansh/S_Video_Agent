# pyrefly: ignore [missing-import]
import os
import requests

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v3")


def transcribe_chunk_sarvam(chunk_path: str, language: str = "english") -> str:
    """Use Sarvam AI API via HTTP requests for transcription."""
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    try:
        print(f"  → Transcribing with Sarvam AI...")
        
        # Sarvam AI Speech-to-Text API endpoint
        url = "https://api.sarvam.ai/speech-to-text"
        
        headers = {
            "api-subscription-key": SARVAM_API_KEY
        }
        
        # Open and send the audio file
        with open(chunk_path, "rb") as audio_file:
            files = {
                "file": audio_file
            }
            data = {
                "model": SARVAM_STT_MODEL,
                "mode": "transcribe"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        # Extract transcript from response
        if "transcript" in result:
            return result["transcript"]
        else:
            return str(result)
                
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

    
    