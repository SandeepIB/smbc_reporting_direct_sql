#!/bin/bash

# SMBC Risk Management Suite - Full Stack Startup Script

set -e  # Exit on any error

echo "🚀 Starting SMBC Risk Management Suite..."

# Kill existing processes on default ports
echo "🔄 Stopping existing processes..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "node.*3000" 2>/dev/null || true
pkill -f "serve.*3000" 2>/dev/null || true
pkill -f "uvicorn.*8000" 2>/dev/null || true

# Kill processes using default ports
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

sleep 2

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run './install.sh' first."
    exit 1
fi

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Backend virtual environment not found. Please run './install.sh' first."
    exit 1
fi

# Check if frontend dependencies exist
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not found. Please run './install.sh' first."
    exit 1
fi

# Function to kill processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server using virtual environment
echo "🔧 Starting backend server on port 8000..."
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start. Check logs above."
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend server started successfully"

# Start frontend development server
echo "🌐 Starting frontend development server on port 3000..."
cd frontend

# Check and fix react-scripts
if [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo "Installing react-scripts..."
    npm install react-scripts@5.0.1 --save-dev --legacy-peer-deps
fi

# Set environment variables to suppress warnings
export GENERATE_SOURCEMAP=false
export SKIP_PREFLIGHT_CHECK=true
export NODE_OPTIONS="--max-old-space-size=4096"

# Start with explicit command
CHOKIDAR_USEPOLLING=false npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 2

echo ""
echo "🎉 SMBC Risk Management Suite is now running in DEVELOPMENT mode!"
echo ""
echo "📱 Web Interface: http://localhost:3000 (Development Server - Live Reload)"
echo "🔧 API Server: http://localhost:8000"
echo "⚙️  Admin Panel: http://localhost:3000 (click gear icon)"
echo ""
echo "📋 Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🔍 Features Available:"
echo "   • Natural Language to SQL Chat Interface"
echo "   • CCR Deck Assistant with Image Analysis"
echo "   • PowerPoint Report Generation"
echo "   • Executive Summary Reports"
echo "   • Admin Dashboard for Feedback Management"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID