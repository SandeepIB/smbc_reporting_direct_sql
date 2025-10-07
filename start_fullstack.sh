#!/bin/bash

echo "🚀 Starting Full-Stack Prompts to Insights Application"
echo "========================================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your database and OpenAI credentials."
    echo "See SETUP.md for details."
    exit 1
fi

# Function to kill processes on port
kill_port() {
    local port=$1
    local pids=$(lsof -ti :$port)
    if [ ! -z "$pids" ]; then
        echo "🔄 Killing existing processes on port $port..."
        echo $pids | xargs kill -9 2>/dev/null
        sleep 2
    fi
}

# Function to find available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    while lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; do
        port=$((port + 1))
    done
    echo $port
}

# Kill existing processes and find available ports
echo "🔄 Checking and cleaning up ports..."
kill_port 8000
kill_port 3000

# Find available ports
BACKEND_PORT=$(find_available_port 8000)
FRONTEND_PORT=$(find_available_port 3000)

echo "✅ Using Backend Port: $BACKEND_PORT"
echo "✅ Using Frontend Port: $FRONTEND_PORT"

# Start backend in background with custom port
echo "🔧 Starting backend API server on port $BACKEND_PORT..."
cd backend
uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null; then
    echo "✅ Backend API is running on http://localhost:$BACKEND_PORT"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend with custom port and backend URL
echo "🎨 Starting frontend React app on port $FRONTEND_PORT..."
cd frontend
PORT=$FRONTEND_PORT REACT_APP_BACKEND_URL=http://localhost:$BACKEND_PORT npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Application started successfully!"
echo "📱 Web Interface: http://localhost:$FRONTEND_PORT"
echo "🔌 API Endpoint: http://localhost:$BACKEND_PORT"
echo "📖 API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "💡 You can also use the CLI:"
echo "   python cli_app.py"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait