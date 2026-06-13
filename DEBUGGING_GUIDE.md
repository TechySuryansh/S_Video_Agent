# Debugging Guide

## 🔍 If the pipeline is still hanging or stuck:

### Step 1: Check FFmpeg Installation
```bash
# Verify FFmpeg is installed
ffmpeg -version

# If not installed on macOS:
brew install ffmpeg

# Check it's in PATH:
which ffmpeg
```

### Step 2: Check API Keys
```bash
# Verify keys are set
cat .env

# Should contain:
# MISTRAL_API_KEY=sk-...
# SARVAM_API_KEY=...
```

### Step 3: Run with Debug Logging
```bash
# Enable debug output
export PYTHONUNBUFFERED=1
python main.py  # Shows all print statements immediately
```

**Expected output for YouTube URL**:
```
starting AI Video Assistant
Downloading: https://www.youtube.com/watch?v=...
[youtube] Downloading video information: ...
✓ Downloaded: downloades/Video_Title.wav
📊 Chunking audio (120.5MB)...
✓ Ready: 12 chunk(s)
Using Whisper for transcription.
Transcribing chunk 1/12...
Transcribing chunk 2/12...
...
raw transcription (first 300 characters) This is a test...
Loading Whisper model: base ...
Whisper model loaded.
Building vector Store
...
```

### Step 4: Check Individual Components

**Test audio download only**:
```python
from utils.audio_processor import download_youtube_audio
result = download_youtube_audio("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(f"Downloaded: {result}")
```

**Test transcription only**:
```python
from utils.audio_processor import process_input
from core.transcriber import transcribe_all

chunks = process_input("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
transcript = transcribe_all(chunks, "english")
print(f"Transcript length: {len(transcript)}")
```

**Test summarization only**:
```python
from core.summarizer import summarize

text = "Your sample transcript..."
summary = summarize(text)
print(summary)
```

---

## 🐛 Common Errors & Fixes

### Error: `FileNotFoundError: Downloaded file not found`

**Cause**: FFmpeg post-processor failed or file path is wrong

**Fix**:
```bash
# Check downloads folder
ls -la downloades/

# Verify FFmpeg paths
brew link ffmpeg --force  # On macOS with Homebrew
```

---

### Error: `socket timeout exceeded`

**Cause**: YouTube server is slow or connection is unstable

**Fix**:
```python
# In audio_processor.py, increase timeout:
"socket_timeout": 60,  # Was 30, now 60 seconds
"retries": 20,         # Increase retry count
```

---

### Error: `SARVAM_API_KEY not found`

**Cause**: Missing environment variable for Hindi transcription

**Fix**:
```bash
# Add to .env
SARVAM_API_KEY=your_api_key_here

# Reload environment
source .env
```

---

### Error: `Streaming body read timeout`

**Cause**: Large file or slow network

**Fix**:
```python
# In transcriber.py, increase Sarvam timeout:
response = requests.post(
    SARVAM_STT_TRANSLATE_URL,
    headers=headers,
    files=files,
    data=data,
    timeout=180,  # Increase from 120 to 180 seconds
)
```

---

### Error: `WhisperModel out of memory`

**Cause**: Using large Whisper model on low-RAM system

**Fix**:
```bash
# Use smaller model
export WHISPER_MODEL=tiny  # default is base

# Or temporarily free RAM
killall Python  # Close other Python processes
```

---

### Error: `timeout=60 (in app.py ThreadPoolExecutor)`

**Cause**: LLM or RAG operation taking >60 seconds

**Fix**:
```python
# In app.py, increase timeout:
title = future_title.result(timeout=120)  # Increase from 60 to 120
```

---

## 🔧 Performance Tuning

### If pipeline is slow:

**1. Use smaller Whisper model** (faster transcription):
```bash
export WHISPER_MODEL=tiny  # ~1min per 10min audio
# vs
export WHISPER_MODEL=base  # ~2min per 10min audio
```

**2. Reduce chunk overlap** (less redundant processing):
```python
# In summarizer.py:
splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=100,  # Was 200
)
```

**3. Reduce vector store k** (fewer context docs):
```python
# In rag_engine.py:
retriever = get_retriever(vector_store, k=2)  # Was 4
```

**4. Cache embeddings** (first RAG query creates index, subsequent are fast):
- Already optimized in current code

---

## 📊 Monitoring & Profiling

### Check memory usage:
```bash
# Monitor in real-time
top -p $(pgrep -f "streamlit run") # Find Python process

# Or
ps aux | grep python | grep -v grep  # Show memory column
```

### Profile a slow function:
```python
import cProfile
import pstats

cProfile.run('summarize(transcript)', 'stats')
p = pstats.Stats('stats')
p.sort_stats('cumulative').print_stats(20)
```

### Time individual steps:
```python
import time

start = time.time()
transcript = transcribe_all(chunks, "english")
print(f"Transcription took {time.time() - start:.1f}s")
```

---

## 🎯 Optimal Configuration

### Recommended `.env` for fastest results:
```bash
# Use smaller models
WHISPER_MODEL=tiny

# API keys (required)
MISTRAL_API_KEY=sk-...
SARVAM_API_KEY=...
```

### Recommended chunking for large videos:
```python
# In audio_processor.py
def chunk_audio(wav_path, chunk_minutes=20):  # Larger chunks = fewer API calls
    ...
```

---

## 📞 Getting Help

1. **Check console output** first - usually tells you exactly what failed
2. **Run `main.py` instead of Streamlit** - clearer error messages
3. **Test components individually** - isolate the problem
4. **Check `.env` file** - most issues are missing API keys
5. **Restart Python kernel** - clears cached models

---

## ✅ Verification Checklist

Before reporting a bug, verify:

- [ ] FFmpeg is installed: `ffmpeg -version`
- [ ] API keys are valid in `.env`
- [ ] Internet connection is stable
- [ ] File path is correct (if using local file)
- [ ] YouTube video is public and not age-restricted
- [ ] Disk space is available (>2GB)
- [ ] Python environment is activated
- [ ] Dependencies installed: `pip install -r Requirements.txt`

