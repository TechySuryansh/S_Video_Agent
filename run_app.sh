#!/bin/bash

# 🎬 AI Video Assistant - Quick Start Script

echo "🎬 Starting AI Video Assistant..."
echo "================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check dependencies (optional)
echo "🔍 Checking dependencies..."
python check_dependencies.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting Streamlit app..."
    echo "📱 The app will open in your browser at: http://localhost:8501"
    echo ""
    echo "To stop the app, press Ctrl+C"
    echo "================================="
    
    # Start Streamlit
    streamlit run app.py
else
    echo "❌ Dependency check failed. Please fix the issues above."
    exit 1
fi