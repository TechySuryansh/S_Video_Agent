from aiohttp import base_protocol
import yt_dlp 
# pyrefly: ignore [missing-import]
import os
import ssl

# Safely handle unverified contexts locally without breaking the network bundle paths
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"

# 💡 REMOVED: CURL_CA_BUNDLE and REQUESTS_CA_BUNDLE blanks to prevent connection pool crashes

# Ensure homebrew paths are in PATH so yt-dlp/ffmpeg can find deno / ffmpeg
for path in ["/opt/homebrew/bin", "/usr/local/bin"]:
    if path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")

# pyrefly: ignore [missing-import]
from pydub import AudioSegment
DOWNLOAD_DIR="downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    """Download audio from YouTube and convert to WAV."""
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,  # Correct key name
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": False,  # Show progress
        "nocheckcertificate": True,
        
        # ─── CONNECTION FIXES ───
        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 30,
        "source_address": "0.0.0.0",  # Forces IPv4
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading: {url}")
            info = ydl.extract_info(url, download=True)
            
            # Get the output filename correctly
            filename_no_ext = ydl.prepare_filename(info)
            base_path = os.path.splitext(filename_no_ext)[0]
            wav_path = base_path + ".wav"
            
            # Verify the file exists
            if not os.path.exists(wav_path):
                raise FileNotFoundError(f"Downloaded file not found: {wav_path}")
            
            print(f"✓ Downloaded: {wav_path}")
            return wav_path
            
    except Exception as e:
        print(f"❌ YouTube download failed: {e}")
        raise

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    # Validate file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")
    
    # Check file size (max 1GB)
    file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    if file_size_mb > 1024:
        raise ValueError(f"File too large: {file_size_mb:.1f}MB (max 1GB)")
    
    try:
        print(f"Converting {input_path} to WAV...")
        output_path = os.path.splitext(input_path)[0] + "_converted.wav"
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)  # 16kHz mono
        audio.export(output_path, format="wav")
        print(f"✓ Converted: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        raise

def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

    
def process_input(source: str) -> list:
    """
    Route input (URL or file) → WAV → chunks.
    Validates input before processing.
    """
    if not source or not isinstance(source, str):
        raise ValueError("Invalid source: must be a non-empty string")
    
    source = source.strip()
    
    try:
        if source.startswith("http://") or source.startswith("https://"):
            wav_path = download_youtube_audio(source)
        else:
            wav_path = convert_to_wav(source)
        
        # Validate WAV file exists and is readable
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"Failed to create WAV: {wav_path}")
        
        print(f"📊 Chunking audio ({os.path.getsize(wav_path) / (1024*1024):.1f}MB)...")
        chunks = chunk_audio(wav_path)
        print(f"✓ Ready: {len(chunks)} chunk(s)")
        return chunks
        
    except Exception as e:
        print(f"❌ Input processing failed: {e}")
        raise