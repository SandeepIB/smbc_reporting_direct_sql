#!/bin/bash

# SMBC Counterparty Risk Assistant - Installation Script
echo "🔧 Installing SMBC Counterparty Risk Assistant..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    echo "Please install pip for Python package management"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r backend/requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps

if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

# Fix vulnerabilities
npm audit fix --force

cd ..

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

# Admin Credentials (for demo)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
EOF
    echo "✅ Created .env file - Please update with your actual configuration"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Update .env file with your OpenAI API key and database credentials"
echo "2. Ensure your MySQL database is running and accessible"
echo "3. Run: ./start_fullstack.sh"
echo ""
echo "📚 For detailed setup instructions, see README.md"