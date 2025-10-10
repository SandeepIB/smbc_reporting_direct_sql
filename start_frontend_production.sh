#!/bin/bash

# Start Frontend in Production Mode
# This script builds and serves the React app for production use

echo "🚀 Starting Frontend in Production Mode..."

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --legacy-peer-deps
fi

# Build the application
echo "🔨 Building React application..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Kill any existing process on port 3000
    echo "🔄 Checking port 3000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    # Serve the built application
    echo "🌐 Starting production server on http://localhost:3000"
    npx serve -s build -l 3000
else
    echo "❌ Build failed! Please check the errors above."
    exit 1
fi