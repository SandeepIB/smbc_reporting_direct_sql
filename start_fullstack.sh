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

echo "✅ Using Backend Port: $BACKEND_PORT (includes CCR)"
echo "✅ Using Frontend Port: $FRONTEND_PORT"

# Start backend in background with custom port
echo "🔧 Starting backend API server on port $BACKEND_PORT..."
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

# Install additional dependencies for CCR functionality
echo "📦 Installing CCR dependencies..."
pip install python-multipart pillow python-pptx > /dev/null 2>&1

# Start the backend server
python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
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

# CCR functionality is now integrated into main backend
echo "✅ CCR functionality integrated into main backend"

# Start frontend with custom port and backend URLs
echo "🎨 Starting frontend React app on port $FRONTEND_PORT..."
cd frontend

# Check if build exists, if not build it
if [ ! -d "build" ]; then
    echo "🔨 Building React application..."
    npm run build
fi

# Set environment variables for API URLs
export REACT_APP_MAIN_API_URL=http://localhost:$BACKEND_PORT
export REACT_APP_CCR_API_URL=http://localhost:$BACKEND_PORT

# Start frontend (try production build first, fallback to dev)
if [ -d "build" ]; then
    echo "🚀 Starting production frontend server..."
    npx serve -s build -l $FRONTEND_PORT &
    FRONTEND_PID=$!
else
    echo "🚀 Starting development frontend server..."
    PORT=$FRONTEND_PORT npm start &
    FRONTEND_PID=$!
fi
cd ..

echo ""
echo "🎉 Application started successfully!"
echo "📱 Web Interface: http://localhost:$FRONTEND_PORT"
echo "🔌 Unified API: http://localhost:$BACKEND_PORT (includes CCR)"
echo "📖 API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "🌍 Available Pages:"
echo "   • Landing: http://localhost:$FRONTEND_PORT"
echo "   • Chat: http://localhost:$FRONTEND_PORT/chat"
echo "   • CCR Assistant: http://localhost:$FRONTEND_PORT/ccr"
echo "   • Admin: http://localhost:$FRONTEND_PORT/admin"
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