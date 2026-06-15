import os
import requests
import json
from mistralai.client import Mistral
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

def get_mistral_client():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set in environment or .env file.")
    return Mistral(api_key=api_key)

def transcribe_audio_groq(mp3_path: str) -> str:
    """
    Transcribes audio using Groq Cloud Whisper API.
    If the file is larger than 24MB, chunks it into 10-minute segments,
    transcribes each segment, and joins the results.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
        
    file_size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
    
    # Check if the file needs chunking (Groq has a 25MB limit)
    if file_size_mb >= 24:
        print(f"📊 Audio file is {file_size_mb:.1f}MB (>= 24MB). Chunking into segments...")
        from utils.audio_processor import chunk_audio
        chunks = chunk_audio(mp3_path, chunk_minutes=10)
        print(f"✓ Spliced into {len(chunks)} chunk(s).")
    else:
        chunks = [mp3_path]
        
    full_transcript = ""
    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(f"🎙️ Transcribing chunk {i+1}/{len(chunks)} via Groq...")
        else:
            print(f"🎙️ Transcribing audio via Groq...")
            
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {groq_api_key}"
        }
        
        with open(chunk, "rb") as f:
            files = {
                "file": (os.path.basename(chunk), f.read(), "audio/mp3")
            }
            data = {
                "model": "whisper-large-v3-turbo",
                "response_format": "json"
            }
            response = requests.post(url, headers=headers, files=files, data=data)
            
        if not response.ok:
            raise RuntimeError(f"Groq API returned error: {response.text}")
            
        chunk_text = response.json().get("text", "")
        full_transcript += chunk_text + " "
        
        # Clean up temporary chunk files if created
        if len(chunks) > 1 and chunk != mp3_path:
            try:
                os.remove(chunk)
            except Exception:
                pass
                
    return full_transcript.strip()

def analyze_audio(audio_path: str) -> dict:
    """
    Transcribes audio using Groq, then analyzes it with Mistral AI,
    returning a dictionary with structured meeting takeaways.
    """
    # 1. Transcribe the audio via Groq
    transcript = transcribe_audio_groq(audio_path)
    
    # Clean up the local MP3 file to save disk space
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"🗑️ Cleaned up local file {os.path.basename(audio_path)}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to delete local file {audio_path}: {e}")
        
    if not transcript:
        raise ValueError("Failed to transcribe the audio. The transcript is empty.")
        
    # 2. Analyze the transcript using Mistral AI
    print("🧠 Extracting structured takeaways via Mistral AI...")
    client = get_mistral_client()
    
    prompt = f"""You are an expert meeting analyst. Analyze the following meeting transcript.
You must return a JSON object with the following JSON format keys:
- "title": A short professional meeting title (max 8 words)
- "summary": A professional meeting summary in bullet points
- "action_items": A numbered list of action items. For each item provide: Task description, Owner (who is responsible), and Deadline (if mentioned, else write 'Not specified'). Format as a numbered list.
- "key_decisions": A numbered list of all key decisions made.
- "open_questions": A numbered list of unresolved questions or topics needing follow-up.

If any category has no items found, write "No [category] found." for that field.

Transcript:
\"\"\"{transcript}\"\"\"
"""
    
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    analysis = json.loads(response.choices[0].message.content)
    
    # Add the transcript back to the dict for the UI display
    analysis["transcript"] = transcript
    return analysis

def ask_question_about_transcript(transcript: str, chat_history: list, question: str) -> str:
    """
    Answers questions about the transcript using Mistral AI.
    """
    client = get_mistral_client()
    
    system_instruction = f"""You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{transcript}"""

    messages = [{"role": "system", "content": system_instruction}]
    for msg in chat_history:
        role = msg["role"]
        # Map roles correctly (mistral uses user/assistant)
        if role == "model":
            role = "assistant"
        messages.append({"role": role, "content": msg["content"]})
        
    messages.append({"role": "user", "content": question})
    
    print(f"💬 Answering question about transcript...")
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content
