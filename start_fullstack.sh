#!/bin/bash

echo "🚀 Starting Full-Stack Natural Language to SQL Application"
echo "========================================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your database and OpenAI credentials."
    echo "See SETUP.md for details."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check ports
if ! check_port 8000; then
    echo "Backend port 8000 is busy. Please stop the existing service or use a different port."
    exit 1
fi

if ! check_port 3000; then
    echo "Frontend port 3000 is busy. Please stop the existing service or use a different port."
    exit 1
fi

echo "✅ Ports 8000 and 3000 are available"

# Start backend in background
echo "🔧 Starting backend API server..."
./run_backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend React app..."
./run_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "🎉 Application started successfully!"
echo "📱 Web Interface: http://localhost:3000"
echo "🔌 API Endpoint: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
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