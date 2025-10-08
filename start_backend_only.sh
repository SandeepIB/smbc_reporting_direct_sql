#!/bin/bash

echo "🚀 Starting Backend API Only"
echo "============================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your database and OpenAI credentials."
    exit 1
fi

# Kill existing backend process
echo "🔄 Cleaning up existing processes..."
pkill -f "uvicorn.*main:app" 2>/dev/null
sleep 2

# Start backend
echo "🔧 Starting backend API server..."
cd backend

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Start the backend server
echo "✅ Starting API server on http://localhost:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload