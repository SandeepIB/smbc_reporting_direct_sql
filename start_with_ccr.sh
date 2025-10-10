#!/bin/bash

echo "🚀 Starting Full-Stack Prompts to Insights with CCR Deck Assistant"
echo "=================================================================="

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use. Killing existing process..."
        kill -9 $(lsof -ti:$1) 2>/dev/null || true
        sleep 2
    fi
}

# Clean up ports
echo "🔄 Checking and cleaning up ports..."
check_port 8000
check_port 8001
check_port 3000

# Set ports
BACKEND_PORT=8000
CCR_BACKEND_PORT=8001
FRONTEND_PORT=3000

echo "✅ Using Main Backend Port: $BACKEND_PORT"
echo "✅ Using CCR Backend Port: $CCR_BACKEND_PORT"
echo "✅ Using Frontend Port: $FRONTEND_PORT"

# Start main backend
echo "🔧 Starting main backend API server on port $BACKEND_PORT..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
MAIN_BACKEND_PID=$!
cd ..

# Wait for main backend to start
sleep 3

# Check if main backend is running
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null; then
    echo "✅ Main Backend API is running on http://localhost:$BACKEND_PORT"
else
    echo "❌ Main Backend failed to start"
    exit 1
fi

# Start CCR backend
echo "🔧 Starting CCR Deck Assistant backend on port $CCR_BACKEND_PORT..."
cd smbc_reporting_tool
python -m uvicorn backend.main:app --host 0.0.0.0 --port $CCR_BACKEND_PORT --reload &
CCR_BACKEND_PID=$!
cd ..

# Wait for CCR backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend React app on port $FRONTEND_PORT..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Application started successfully!"
echo "📱 Web Interface: http://localhost:$FRONTEND_PORT"
echo "🔌 Main API: http://localhost:$BACKEND_PORT"
echo "🔌 CCR API: http://localhost:$CCR_BACKEND_PORT"
echo "📖 API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "💡 Features available:"
echo "   - Chat Interface (💬 button)"
echo "   - CCR Deck Assistant (navigation menu)"
echo "   - Admin Interface (⚙️ gear icon in chat)"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $MAIN_BACKEND_PID 2>/dev/null || true
    kill $CCR_BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    
    # Kill any remaining processes on the ports
    kill -9 $(lsof -ti:$BACKEND_PORT) 2>/dev/null || true
    kill -9 $(lsof -ti:$CCR_BACKEND_PORT) 2>/dev/null || true
    kill -9 $(lsof -ti:$FRONTEND_PORT) 2>/dev/null || true
    
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait