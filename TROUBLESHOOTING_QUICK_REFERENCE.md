# 🚨 Troubleshooting Quick Reference

## Symptom → Solution

### "Pipeline is hanging/stuck"
```bash
# 1. Check FFmpeg
ffmpeg -version

# 2. Check API keys
cat .env | grep -E "MISTRAL|SARVAM"

# 3. Kill and restart with debug
export PYTHONUNBUFFERED=1
python3 main.py
```
**Then watch console output carefully** - it will show exactly where it gets stuck.

---

### "File not found after download"
**Cause**: FFmpeg not installed or in wrong PATH

```bash
# Check if FFmpeg is installed
which ffmpeg

# If not found, install it
brew install ffmpeg

# Verify installation
ffmpeg -version
```

---

### "Transcription returns empty string"
**Cause**: Audio quality, language, or model issue

```bash
# Try a different video or Whisper model
export WHISPER_MODEL=base  # Better quality

# Or switch to Hinglish if video is in Hindi
# Set language: hinglish
```

---

### "TimeoutError: result() took too long"
**Cause**: LLM or transcription service is slow

**Fix in `app.py`**:
```python
# Line ~95: Increase timeout
title = future_title.result(timeout=120)  # Was 60, now 120
summary = future_summary.result(timeout=120)
```

---

### "API key not found" or "Authentication failed"
**Cause**: Missing or invalid `.env` file

```bash
# Check .env exists
ls -la .env

# Check keys are set
cat .env

# Should show:
# MISTRAL_API_KEY=sk-...
# SARVAM_API_KEY=...

# If keys are invalid, regenerate them:
# Visit https://console.mistral.ai
# Visit https://console.sarvam.ai
```

---

### "YouTube video access denied"
**Cause**: Video is age-restricted or blocked

**Solutions**:
1. Try a different video
2. Use a local file instead: `python3 main.py` → Enter local path
3. Check if video is public (not private/unlisted)

---

### "ModuleNotFoundError: No module named 'streamlit'"
**Cause**: Dependencies not installed

```bash
# Reinstall all requirements
pip3 install -r Requirements.txt --force-reinstall

# Verify installation
python3 -c "import streamlit; print('✓ OK')"
```

---

### "Connection refused" or "Network error"
**Cause**: Internet connectivity issue

```bash
# Test internet
ping google.com

# Test YouTube connectivity
curl -I https://www.youtube.com

# Check if behind proxy (corporate)
echo $http_proxy
echo $https_proxy
```

---

### "Out of memory" error
**Cause**: Large video or too many parallel processes

```bash
# Use smaller Whisper model
export WHISPER_MODEL=tiny  # Much lighter

# Or process shorter videos first

# Check available memory
vm_stat  # macOS
# or
free -h  # Linux
```

---

### "TypeError: transcribe_chunk_whisper() got unexpected argument"
**Cause**: Code version mismatch

```bash
# Force reinstall package
pip3 install openai-whisper --force-reinstall --no-cache-dir
```

---

## 🔧 Quick Configuration Changes

### Make transcription faster:
```bash
# Add to shell profile (.zshrc or .bash_profile)
export WHISPER_MODEL=tiny
```

### Make transcription more accurate:
```bash
export WHISPER_MODEL=base  # Good balance
# or
export WHISPER_MODEL=small # Best accuracy (slower)
```

### Switch language:
```
Streamlit: Select "hinglish" in sidebar
CLI: Enter "hinglish" when prompted
```

### Increase API timeouts:
**In `utils/audio_processor.py`**:
```python
"socket_timeout": 60,  # Was 30
"retries": 20,        # Was 10
```

---

## 📊 Performance Baseline

If pipeline is slower than this, something's wrong:

| Operation | Expected Time | If Slower → |
|-----------|--------------|-----------|
| YouTube download (10 min video) | 1-3 min | Check internet + video bitrate |
| Whisper transcription (10 min audio) | 3-5 min | Use `WHISPER_MODEL=tiny` |
| Title generation | 20-30 sec | Check API rate limits |
| Summarization | 30-60 sec | Check API rate limits |
| Extraction (3 parallel) | 30-60 sec | Check API rate limits |
| RAG setup | 10-20 sec | Check disk I/O |
| **Total (10 min video)** | **6-15 min** | Something is wrong if >15 min |

---

## 🧪 Test Commands

### Test each component independently:

**Test audio download:**
```python
from utils.audio_processor import download_youtube_audio
wav = download_youtube_audio("https://youtube.com/watch?v=dQw4w9WgXcQ")
print(f"Downloaded: {wav}")
```

**Test transcription:**
```python
from utils.audio_processor import process_input
from core.transcriber import transcribe_all

chunks = process_input("https://youtube.com/watch?v=dQw4w9WgXcQ")
text = transcribe_all(chunks, "english")
print(f"Transcript length: {len(text)} chars")
```

**Test summarization:**
```python
from core.summarizer import summarize
result = summarize("sample text about a meeting...")
print(result)
```

**Test RAG:**
```python
from core.rag_engine import build_rag_chain, ask_question
chain = build_rag_chain("sample transcript...")
answer = ask_question(chain, "What was discussed?")
print(answer)
```

---

## 🆘 If All Else Fails

1. **Clear cache**:
   ```bash
   rm -rf ~/.cache/torch_hub/
   rm -rf ~/.cache/pip/
   rm -rf vector_db/
   ```

2. **Reset environment**:
   ```bash
   deactivate  # Exit virtual env
   python3 -m venv .venv  # Create new one
   source .venv/bin/activate
   pip install -r Requirements.txt
   ```

3. **Check system resources**:
   ```bash
   # Check disk space (need >2GB free)
   df -h
   
   # Check memory (need >4GB free)
   vm_stat | grep "Pages free"
   ```

4. **Last resort - restart everything**:
   ```bash
   killall python3
   sleep 2
   python3 main.py  # Fresh start
   ```

---

## 📞 Getting Help

When reporting issues, include:
1. Full error message (copy-paste from terminal)
2. First 100 characters of console output
3. Your OS and Python version: `python3 --version`
4. FFmpeg version: `ffmpeg -version`
5. YouTube URL that failed

---

## ✅ Healthy System Checklist

```
✓ FFmpeg installed and in PATH
✓ Python 3.8+ installed
✓ API keys in .env and valid
✓ Internet connection working
✓ 2GB+ disk space available
✓ 4GB+ RAM available
✓ Dependencies installed (pip list | grep -E "streamlit|langchain")
✓ No VPN/proxy issues (if corporate network)
```

If all ✓, your system is ready. If any ✗, fix that first.

---

**Happy troubleshooting! 🎯**

