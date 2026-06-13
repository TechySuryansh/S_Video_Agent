# 🎬 AI Video Assistant

An intelligent video analysis tool that transcribes, summarizes, and enables chat interaction with YouTube videos and local audio/video files.

## ✨ Features

- **Multi-format Support**: YouTube URLs and local video/audio files
- **Smart Transcription**: Whisper (English) + Sarvam AI (Hinglish)
- **Intelligent Analysis**: Auto-generated summaries, action items, and key decisions
- **RAG Chat**: Ask questions about your video content
- **Modern UI**: Clean Streamlit interface with real-time progress tracking

## 🚀 Quick Setup

### 1. System Dependencies

**macOS:**
```bash
# Install ffmpeg (required for audio processing)
brew install ffmpeg

# If you don't have Homebrew:
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg python3-dev build-essential
```

**Windows:**
```bash
# Install ffmpeg via chocolatey or download from https://ffmpeg.org/
choco install ffmpeg
```

### 2. Python Environment

```bash
# Clone and navigate to project
git clone <your-repo-url>
cd S_Video_Agent

# Create virtual environment (Python 3.10+ recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file with your API keys:

```env
# Whisper Model (optional, defaults to "small")
WHISPER_MODEL=small

# Sarvam AI for Hinglish transcription (optional)
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_STT_MODEL=saaras:v2.5

# Mistral AI for LLM tasks
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 🛠 Troubleshooting

### Common Issues

**`ModuleNotFoundError: pyaudioop`**
- This is a pydub dependency issue. Try:
  ```bash
  pip install pydub[scipy]
  # Or on some systems:
  pip install pyaudio
  ```

**`ffmpeg not found`**
- Make sure ffmpeg is installed and in your PATH
- On macOS: `brew install ffmpeg`
- Test with: `ffmpeg -version`

**YouTube download fails**
- Some videos are region-restricted or have download protection
- Try uploading the audio file directly instead
- Check if yt-dlp needs updating: `pip install --upgrade yt-dlp`

**Memory issues with large files**
- The app automatically chunks audio into 10-minute segments
- For very large files, consider pre-processing with shorter segments

## 📝 Usage

1. **Input**: Paste a YouTube URL or local file path
2. **Language**: Choose English (Whisper) or Hinglish (Sarvam AI)
3. **Analyze**: Click the analyze button and wait for processing
4. **Explore**: Review the summary, action items, and decisions
5. **Chat**: Ask questions about the content using the RAG system

## 🏗 Architecture

- **Frontend**: Streamlit with custom CSS
- **Transcription**: OpenAI Whisper + Sarvam AI
- **LLM**: Mistral AI via LangChain
- **Vector Store**: ChromaDB with HuggingFace embeddings
- **Audio Processing**: yt-dlp + pydub + ffmpeg

## 🔧 Development

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Format code
black .
isort .
```

## 📄 License

MIT License - see LICENSE file for details
