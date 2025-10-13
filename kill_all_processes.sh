#!/bin/bash

echo "🛑 Killing all SMBC application processes..."

# Kill all Python processes (backend)
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "python.*uvicorn" 2>/dev/null || true

# Kill all Node processes (frontend)
pkill -f "node.*3000" 2>/dev/null || true
pkill -f "node.*3001" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
pkill -f "serve.*build" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true

# Kill processes using specific ports
for port in 3000 3001 8000 8001 5000 5001; do
    echo "Killing processes on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done

# Wait for processes to terminate
sleep 3

echo "✅ All processes killed. Memory freed."
echo "Run ./start_fullstack.sh to start with default ports only."