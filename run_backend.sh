#!/bin/bash

echo "Starting Natural Language to SQL Backend API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r backend/requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create it with your database and OpenAI credentials."
    echo "See SETUP.md for details."
    exit 1
fi

# Start the backend server with auto-reload
echo "Starting FastAPI server on http://localhost:8000 (with auto-reload)"
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload