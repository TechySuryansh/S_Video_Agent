# Quick Start Guide

## 🚀 Get Running in 2 Minutes

### Prerequisites
```bash
# 1. Install FFmpeg (if not already installed)
brew install ffmpeg

# 2. Install Python dependencies
pip install -r Requirements.txt

# 3. Verify API keys in .env
cat .env
# Should have: MISTRAL_API_KEY and SARVAM_API_KEY
```

---

## 🎬 Option A: Web UI (Streamlit)

### Start the app:
```bash
streamlit run app.py
```

**Then**:
1. Open http://localhost:8501 in your browser
2. Paste a YouTube URL or file path in the sidebar
3. Select language (English or Hinglish)
4. Click "⚡ Analyse"
5. Watch the pipeline progress in the sidebar
6. Once done, view results and chat with your meeting!

**Example URLs to test**:
- `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `https://www.youtube.com/watch?v=9bZkp7q19f0`

---

## 🎯 Option B: CLI (Terminal)

### Run analysis:
```bash
python main.py
```

**Follow prompts**:
```
Enter YouTube URL or local file path: https://www.youtube.com/watch?v=...
Language (english/hinglish) [default: english]: english
```

**Then**:
- Watch each stage complete
- See title, summary, action items, decisions, questions
- Chat with the transcript interactively
- Type `exit` to quit

---

## 📁 Option C: Local Audio File

### Instead of YouTube URL:
```
Enter YouTube URL or local file path: /path/to/your/file.mp4
```

Supported formats: `.mp4`, `.wav`, `.mp3`, `.m4a`, `.flac`, etc.

---

## 🔧 Configuration

### Change Whisper model (faster vs. more accurate):
```bash
export WHISPER_MODEL=tiny   # Fastest (9% error rate)
# or
export WHISPER_MODEL=base   # Better (6% error rate) - DEFAULT
# or  
export WHISPER_MODEL=small  # Best (5% error rate) - Slower
```

### Change language:
```bash
# English (offline, fast)
Language selection: english

# Hinglish (online, translates to English)
Language selection: hinglish
```

---

## ✅ What to Expect

### Processing Times (for 1-hour video):

| Stage | Time | Notes |
|-------|------|-------|
| Download + Convert | 2-5 min | Depends on video length & internet |
| Transcription | 5-15 min | Whisper base model |
| Title + Summary | 1-2 min | LLM processing |
| Extraction | 1-2 min | 3 parallel LLM calls |
| RAG Setup | 30 sec | Vector embeddings |
| **Total** | **10-25 min** | Faster with smaller models |

### Output Format:

```
📌 Title: "Quick Summary of Meeting Content"

📋 Summary:
• Key point 1
• Key point 2
• Key point 3

✅ Action Items:
1. Task description - Owner: Name - Deadline: Date
2. ...

🔑 Key Decisions:
1. Decision 1
2. ...

❓ Open Questions:
1. Question 1
2. ...
```

---

## 💬 Chat with Your Meeting

After analysis completes, ask questions:

```
You: What were the main decisions?
🤖 Assistant: The main decisions were...

You: Who is responsible for action item 1?
🤖 Assistant: Based on the transcript...

You: exit
👋 Goodbye!
```

---

## 🐛 Troubleshooting

### "Pipeline hanging" or "No output"
```bash
# 1. Check if FFmpeg is installed
ffmpeg -version

# 2. Check API keys
cat .env

# 3. Run with debug output
export PYTHONUNBUFFERED=1
python main.py
```

### "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install -r Requirements.txt --force-reinstall
```

### "YouTube access error"
```bash
# Try a different video or URL
# Some videos are age-restricted or blocked

# Or use a local file instead
python main.py
# Enter local file path when prompted
```

### "Transcription is empty"
```bash
# The audio may be too quiet or in an unsupported language
# Try another video or enable debug logging
export PYTHONUNBUFFERED=1
python main.py
```

---

## 📊 Performance Tips

### Speed up processing:
```bash
# Use tiny Whisper model (fastest)
export WHISPER_MODEL=tiny

# Use CLI instead of web UI
python main.py
```

### Better accuracy (slower):
```bash
# Use base or small Whisper model
export WHISPER_MODEL=base  # Recommended
export WHISPER_MODEL=small # Best quality
```

---

## 🎓 Learn More

- **DEBUGGING_GUIDE.md**: Detailed troubleshooting
- **FIXES_APPLIED.md**: What was fixed in your pipeline
- **README.md**: Full project documentation

---

## ❤️ Next Steps

1. ✅ Test with a sample YouTube video
2. ✅ Try different languages
3. ✅ Use the chat interface to ask questions
4. ✅ Analyze your own meeting videos

**Enjoy! 🚀**

