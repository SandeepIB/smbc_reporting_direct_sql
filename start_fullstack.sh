#!/bin/bash

# SMBC Counterparty Risk Assistant - Full Stack Startup Script
echo "🚀 Starting SMBC Counterparty Risk Assistant..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create .env file with your configuration."
    echo "📝 Copy .env.example to .env and update with your settings."
    exit 1
fi

# Install backend dependencies if needed
echo "📦 Checking backend dependencies..."
if [ ! -d "backend/__pycache__" ] || [ ! -f "backend/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r backend/requirements.txt
fi

# Install frontend dependencies if needed
echo "📦 Checking frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install --legacy-peer-deps
    npm audit fix --force
fi

# Build frontend for production
echo "🔨 Building frontend..."
npm run build

cd ..

# Function to kill processes on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
echo "🔧 Starting backend server on port 8000..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start. Check logs above."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend server started successfully"

# Start frontend server
echo "🌐 Starting frontend server on port 3000..."
cd frontend
npx serve -s build -l 3000 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 2

echo ""
echo "🎉 SMBC Counterparty Risk Assistant is now running!"
echo ""
echo "📱 Web Interface: http://localhost:3000"
echo "🔧 API Server: http://localhost:8000"
echo "⚙️  Admin Panel: http://localhost:3000 (click gear icon)"
echo ""
echo "📋 Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID