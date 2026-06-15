#!/usr/bin/env python3
"""
Dependency checker for S_Video_Agent
Run this script to verify all required dependencies are properly installed.
"""

import sys
import subprocess
from typing import List, Tuple

def check_import(module_name: str, import_statement: str = None) -> Tuple[bool, str]:
    """Check if a module can be imported successfully."""
    if import_statement is None:
        import_statement = f"import {module_name}"
    
    try:
        exec(import_statement)
        return True, "✅ OK"
    except ImportError as e:
        return False, f"❌ FAILED: {e}"
    except Exception as e:
        return False, f"❌ ERROR: {e}"

def check_system_command(command: str) -> Tuple[bool, str]:
    """Check if a system command is available."""
    try:
        # Different commands use different version flags
        version_flags = {
            "ffmpeg": ["-version"],
            "python3": ["--version"],
        }
        
        flags = version_flags.get(command, ["--version"])
        result = subprocess.run([command] + flags, 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, "✅ OK"
        else:
            return False, f"❌ Command failed: {result.stderr.strip()}"
    except FileNotFoundError:
        return False, f"❌ Command not found: {command}"
    except Exception as e:
        return False, f"❌ ERROR: {e}"

def main():
    """Run all dependency checks."""
    print("🔍 S_Video_Agent Dependency Checker")
    print("=" * 50)
    
    # Core Python modules
    python_checks = [
        ("os", None),
        ("ssl", None), 
        ("subprocess", None),
        ("requests", None),
    ]
    
    # Audio processing
    audio_checks = [
        ("pydub", "from pydub import AudioSegment"),
        ("whisper", "import whisper"),
        ("torch", "import torch"),
        ("torchaudio", "import torchaudio"),
        ("numpy", "import numpy as np"),
        ("scipy", "import scipy"),
    ]
    
    # LangChain and ML
    ml_checks = [
        ("langchain_core", "from langchain_core.documents import Document"),
        ("langchain_community", "from langchain_community.embeddings import HuggingFaceEmbeddings"),
        ("langchain_mistralai", "from langchain_mistralai import ChatMistralAI"),
        ("mistralai", "import mistralai"),
        ("sentence_transformers", "from sentence_transformers import SentenceTransformer"),
        ("chromadb", "import chromadb"),
        ("langchain_chroma", "from langchain_chroma import Chroma"),
        ("huggingface_hub", "from huggingface_hub import HfApi"),
    ]
    
    # Web and UI
    web_checks = [
        ("streamlit", "import streamlit as st"),
        ("yt_dlp", "import yt_dlp"),
        ("dotenv", "try:\n    from dotenv import load_dotenv\nexcept ImportError:\n    pass"),
    ]
    
    # System commands
    system_checks = [
        "ffmpeg",
        "python3",
    ]
    
    all_passed = True
    
    # Run Python import checks
    for section_name, checks in [
        ("Core Python", python_checks),
        ("Audio Processing", audio_checks), 
        ("Machine Learning", ml_checks),
        ("Web & UI", web_checks),
    ]:
        print(f"\n📦 {section_name}:")
        for module, import_stmt in checks:
            success, message = check_import(module, import_stmt)
            print(f"  {module:20} {message}")
            if not success:
                all_passed = False
    
    # Run system command checks
    print(f"\n🔧 System Commands:")
    for command in system_checks:
        success, message = check_system_command(command)
        print(f"  {command:20} {message}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All dependencies are properly installed!")
        print("✅ You should be able to run the app with: streamlit run app.py")
    else:
        print("⚠️  Some dependencies are missing or broken.")
        print("📋 Install missing packages with: pip install -r requirements.txt")
        print("🔧 For system commands, check the README.md for installation instructions")
        sys.exit(1)

if __name__ == "__main__":
    main()