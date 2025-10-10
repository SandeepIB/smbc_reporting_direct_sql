#!/bin/bash

# Fix Backend Dependencies
# This script installs missing Python dependencies for the unified backend

echo "🔧 Fixing Backend Dependencies..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install all requirements
echo "📦 Installing main requirements..."
pip install -r requirements.txt

# Install specific missing dependencies that commonly cause issues
echo "📦 Installing additional dependencies..."
pip install python-multipart pillow python-pptx

# Verify installations
echo "✅ Verifying installations..."
python -c "import fastapi; print('FastAPI: OK')"
python -c "import multipart; print('python-multipart: OK')" 2>/dev/null || echo "⚠️ python-multipart: Not found"
python -c "from PIL import Image; print('Pillow: OK')" 2>/dev/null || echo "⚠️ Pillow: Not found"
python -c "from pptx import Presentation; print('python-pptx: OK')" 2>/dev/null || echo "⚠️ python-pptx: Not found"

echo "✅ Backend dependencies fixed!"
echo "💡 You can now run: ./start_fullstack.sh"