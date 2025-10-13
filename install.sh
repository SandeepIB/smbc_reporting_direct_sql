#!/bin/bash

# SMBC Risk Management Suite Installation Script

set -e  # Exit on any error

echo "🚀 Installing SMBC Risk Management Suite..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+"
    exit 1
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps
npm audit fix --force || true

# Build frontend for production
echo "🔨 Building frontend..."
npm run build
cd ..

# Make scripts executable
chmod +x *.sh

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env configuration file..."
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name

# Application Settings
ROW_LIMIT=500
ALLOWED_SCHEMAS=
ALLOWED_TABLES=
EOF
    echo "✅ Created .env file - Please update with your actual configuration"
fi

echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your OpenAI API key and database credentials"
echo "2. Run './start_fullstack.sh' to start the application"
echo "3. Access the app at http://localhost:3000"
echo ""
echo "📖 For detailed setup instructions, see README.md"