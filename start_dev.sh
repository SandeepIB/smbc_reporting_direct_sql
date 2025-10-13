#!/bin/bash

echo "🚀 Starting SMBC Development Environment..."

# Kill existing processes
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Function to kill processes on exit
cleanup() {
    echo "🛑 Shutting down development servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend in development mode with auto-reload
echo "🔧 Starting backend server (dev mode)..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 2

# Start frontend in development mode
echo "🌐 Starting frontend server (dev mode)..."
cd frontend
FAST_REFRESH=true npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Development Environment Running!"
echo ""
echo "📱 Frontend (Hot Reload): http://localhost:3000"
echo "🔧 Backend (Auto Reload): http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep running
wait $BACKEND_PID $FRONTEND_PID