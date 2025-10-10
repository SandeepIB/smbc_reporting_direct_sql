#!/bin/bash

# Debug Frontend Issues
# This script helps diagnose and fix common frontend problems

echo "🔍 Debugging Frontend Issues..."

# Check if port 3000 is in use
echo "📡 Checking port 3000..."
PORT_CHECK=$(lsof -i :3000 2>/dev/null)
if [ ! -z "$PORT_CHECK" ]; then
    echo "⚠️  Port 3000 is in use:"
    echo "$PORT_CHECK"
    echo ""
    read -p "Kill processes on port 3000? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
        echo "✅ Processes killed"
    fi
else
    echo "✅ Port 3000 is free"
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
echo "📦 Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found. Installing..."
    npm install --legacy-peer-deps
else
    echo "✅ Dependencies found"
fi

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory!"
    exit 1
fi

# Try to build the application
echo "🔨 Testing build process..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Offer to start the application
    echo ""
    echo "Choose how to start the frontend:"
    echo "1) Development server (npm start)"
    echo "2) Production server (serve build)"
    echo "3) Exit"
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            echo "🚀 Starting development server..."
            npm start
            ;;
        2)
            echo "🚀 Starting production server..."
            npx serve -s build -l 3000
            ;;
        3)
            echo "👋 Exiting..."
            exit 0
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
else
    echo "❌ Build failed! Check the errors above."
    echo ""
    echo "Common fixes:"
    echo "1. Clear cache: npm cache clean --force"
    echo "2. Reinstall: rm -rf node_modules package-lock.json && npm install --legacy-peer-deps"
    echo "3. Check Node.js version: node --version (should be 16+)"
    exit 1
fi