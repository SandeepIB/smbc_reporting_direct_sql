#!/bin/bash

echo "🚀 Starting SMBC Unified Application (Chat + CCR)..."

# Kill any existing processes
echo "🔄 Stopping existing processes..."
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
sleep 2

# Start backend (unified API on port 8000)
echo "🔧 Starting unified backend on port 8000..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend started successfully"

# Start frontend
echo "🎨 Starting frontend on port 3000..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 10

echo ""
echo "🎉 SMBC Unified Application is running!"
echo ""
echo "📱 Access Points:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • Chat Interface: http://localhost:3000/chat"
echo "   • CCR Assistant: http://localhost:3000/ccr"
echo "   • Admin Panel: http://localhost:3000/admin"
echo ""
echo "🔧 API Endpoints:"
echo "   • Chat: POST /chat"
echo "   • CCR Upload: POST /upload-images"
echo "   • CCR Analyze: POST /analyze"
echo "   • Health Check: GET /health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0' INT
wait