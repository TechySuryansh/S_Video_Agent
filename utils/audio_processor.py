from aiohttp import base_protocol
import yt_dlp 
# pyrefly: ignore [missing-import]
import os
import ssl
import subprocess

# Safely handle unverified contexts locally without breaking the network bundle paths
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PYTHONHTTPSVERIFY"] = "0"

# 💡 REMOVED: CURL_CA_BUNDLE and REQUESTS_CA_BUNDLE blanks to prevent connection pool crashes

# Ensure homebrew paths are in PATH so yt-dlp/ffmpeg can find deno / ffmpeg
for path in ["/opt/homebrew/bin", "/usr/local/bin"]:
    if path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")

DOWNLOAD_DIR="downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    """Download audio from YouTube and convert to WAV."""
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    # Try multiple strategies to bypass 403
    strategies = [
        # Strategy 1: Android client (most reliable)
        {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }],
            "quiet": False,
            "nocheckcertificate": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"],
                }
            },
        },
        # Strategy 2: iOS client
        {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }],
            "quiet": False,
            "nocheckcertificate": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["ios"],
                }
            },
        },
        # Strategy 3: Web with enhanced headers
        {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }],
            "quiet": False,
            "nocheckcertificate": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
            }
        }
    ]
    
    last_error = None
    for i, ydl_opts in enumerate(strategies, 1):
        try:
            print(f"Attempting download strategy {i}/{len(strategies)}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                filename_no_ext = ydl.prepare_filename(info)
                base_path = os.path.splitext(filename_no_ext)[0]
                wav_path = base_path + ".wav"
                
                if not os.path.exists(wav_path):
                    raise FileNotFoundError(f"Downloaded file not found: {wav_path}")
                
                print(f"✓ Downloaded: {wav_path}")
                return wav_path
                
        except Exception as e:
            last_error = e
            print(f"Strategy {i} failed: {str(e)[:100]}")
            continue
    
    # All strategies failed
    error_msg = f"All download strategies failed. Last error: {last_error}"
    print(f"❌ {error_msg}")
    
    # Provide helpful error message
    if "403" in str(last_error) or "Forbidden" in str(last_error):
        raise RuntimeError(
            "YouTube blocked the download (403 Forbidden). "
            "This video may be restricted or rate-limited. "
            "Try: 1) A different video, 2) Wait a few minutes, or 3) Upload the audio file directly instead."
        )
    else:
        raise RuntimeError(error_msg)

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using ffmpeg."""
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
        
        # Use ffmpeg to convert to 16kHz mono WAV
        subprocess.run([
            "ffmpeg", "-i", input_path,
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",  # mono
            "-y",  # overwrite
            output_path
        ], check=True, capture_output=True)
        
        print(f"✓ Converted: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg conversion failed: {e.stderr.decode() if e.stderr else str(e)}")
        raise
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        raise

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """Chunk audio file into segments using ffmpeg."""
    try:
        # Get audio duration
        result = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            wav_path
        ], capture_output=True, text=True, check=True)
        
        duration_seconds = float(result.stdout.strip())
        chunk_seconds = chunk_minutes * 60
        
        chunks = []
        chunk_count = int((duration_seconds + chunk_seconds - 1) / chunk_seconds)
        
        for i in range(chunk_count):
            start_time = i * chunk_seconds
            chunk_path = f"{wav_path}_chunk_{i}.wav"
            
            # Extract chunk using ffmpeg
            subprocess.run([
                "ffmpeg", "-i", wav_path,
                "-ss", str(start_time),
                "-t", str(chunk_seconds),
                "-c", "copy",
                "-y",
                chunk_path
            ], check=True, capture_output=True)
            
            chunks.append(chunk_path)
        
        return chunks
        
    except Exception as e:
        print(f"❌ Audio chunking failed: {e}")
        # If chunking fails, return the whole file
        return [wav_path]

    
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