# 🚀 Deployment Guide

## Streamlit Cloud Deployment

### 1. Repository Setup
Make sure your repository contains:
- `requirements.txt` (Python dependencies)
- `packages.txt` (System dependencies) 
- `.streamlit/config.toml` (Streamlit configuration)
- `.env.example` (Environment variables template)

### 2. Environment Variables
In Streamlit Cloud dashboard, go to "Settings" → "Secrets" and set these environment variables:

**Required:**
```toml
MISTRAL_API_KEY = "your_mistral_api_key_here"
```

**Optional:**
```toml
WHISPER_MODEL = "small"
SARVAM_API_KEY = "your_sarvam_api_key_here" 
SARVAM_STT_MODEL = "saaras:v2.5"
```

**Note:** Streamlit Cloud uses TOML format for secrets, not dotenv format.

### 3. Known Issues & Solutions

#### `ModuleNotFoundError: aiohttp`
This was caused by an unnecessary import in the audio processor.

**Solution**: The import has been removed as it was not used by the application.

#### `ModuleNotFoundError: dotenv`
This occurs when python-dotenv is not available in the deployment environment.

**Solution**: The app now includes automatic fallback handling. If you see this error:
1. The app will automatically use environment variables directly
2. Make sure you've set the environment variables in Streamlit Cloud secrets
3. No action needed - the fallback should work automatically

#### `ModuleNotFoundError: pyaudioop`
This affects pydub on some deployment environments.

**Solution 1**: The app includes automatic fallback to ffmpeg-only processing
**Solution 2**: Add these to `packages.txt`:
```
libsndfile1
portaudio19-dev
python3-dev
build-essential
```

**Solution 3**: If pydub still fails, set this environment variable:
```
PYDUB_FALLBACK = "true"
```

#### `ffmpeg not found`
**Solution**: `packages.txt` already includes ffmpeg installation

#### Memory Issues
Large files might cause memory issues on Streamlit Cloud's free tier.
**Solution**: 
- Use shorter audio files (< 100MB)
- Pre-process large files locally before upload
- Consider upgrading to Streamlit Cloud Pro

#### YouTube Download Blocked
Some videos are region-locked or have download protection.
**Solution**: 
- Use the file upload option instead
- Try different video sources
- Use yt-dlp locally to download first, then upload

### 4. Alternative Deployment Options

#### Docker Deployment
```bash
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

#### Railway/Render Deployment
1. Connect GitHub repository
2. Set environment variables
3. Use these build commands:
   ```bash
   pip install -r requirements.txt
   ```
4. Start command:
   ```bash
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

### 5. Performance Optimization

#### For Production Deployment:
1. Use smaller Whisper models (`tiny`, `base` instead of `small`)
2. Implement chunking limits (max 50MB files)
3. Add caching for embeddings and models
4. Use async processing for long tasks
5. Add progress indicators and error handling

#### Resource Requirements:
- **Minimum**: 2GB RAM, 1 CPU core
- **Recommended**: 4GB RAM, 2 CPU cores
- **Storage**: ~2GB for models and cache

### 6. Monitoring & Debugging

#### Enable Debug Logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check System Resources:
```python
import psutil
print(f"Memory: {psutil.virtual_memory()}")
print(f"CPU: {psutil.cpu_percent()}")
```

#### Test Dependencies:
```bash
python check_dependencies.py
```

### 7. Security Considerations

- Never commit API keys to repository
- Use Streamlit secrets management
- Validate file uploads (size, format)
- Implement rate limiting for API calls
- Consider using environment-specific configs

### 8. Scaling Considerations

For high-traffic usage:
- Use dedicated compute instances
- Implement Redis caching
- Use queue-based processing (Celery)
- Consider microservices architecture
- Use CDN for static assets