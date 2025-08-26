#!/bin/bash

echo "🚀 Starting React frontend..."

cd frontend

# Check if react-scripts exists
if ! npm list react-scripts > /dev/null 2>&1; then
    echo "📦 Installing react-scripts..."
    npm install react-scripts@5.0.1 --save
fi

# Start the development server
npm start