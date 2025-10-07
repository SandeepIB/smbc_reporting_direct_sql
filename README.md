# Prompts to Insights Application

A full-stack application that converts natural language prompts into actionable insights by generating SQL queries and executing them against a MySQL database. Available as both CLI and web interface.

## Features

### Core Features
- **Cacheable Schema Generation**: Generate database schema once and reuse
- **Natural Language Processing**: Convert prompts to insights using OpenAI
- **Safe Query Execution**: Execute queries with proper error handling
- **Session Management**: Multi-user support with chat history

### Interface Options
- **Web Interface**: Modern React-based chat interface
- **CLI Interface**: Interactive command-line tool
- **REST API**: FastAPI backend for integration

## Setup

1. Install backend dependencies:
```bash
pip install -r requirements.txt
```

2. Setup frontend (with security fixes):
```bash
# Option 1: Complete setup with security fixes
./setup_frontend.sh

# Option 2: Quick vulnerability fix (if already installed)
./fix_npm_vulnerabilities.sh

# Option 3: Manual setup
cd frontend
npm install --legacy-peer-deps
npm audit fix
```

2. Configure environment variables in `.env`:
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

# Behavior
ROW_LIMIT=500
ALLOWED_SCHEMAS=
ALLOWED_TABLES=
```

## Quick Start

### Full-Stack Application (Recommended)
```bash
# Start both backend API and frontend web interface
./start_fullstack.sh
```

Then open http://localhost:3000 in your browser.

### CLI Only
```bash
# Interactive mode
python cli_app.py

# Single question
python cli_app.py "How many users are in the system?"

# Test connection
python cli_app.py test-connection
```

### Backend API Only
```bash
# Start FastAPI server
./run_backend.sh
```

API will be available at http://localhost:8000

### Frontend Only
```bash
# Start React development server
./run_frontend.sh
```

Web interface will be available at http://localhost:3000

## File Structure

```
├── backend/                    # FastAPI backend
│   ├── main.py                # API server
│   ├── chatbot_service.py     # Core chatbot logic
│   └── requirements.txt       # Backend dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   └── services/          # API services
│   └── package.json           # Frontend dependencies
├── src/                       # Core modules (shared)
│   ├── core/                  # Configuration
│   ├── services/              # Database, AI, Schema services
│   └── utils/                 # Utilities
├── cli_app.py                 # CLI application
├── app.py                     # Legacy CLI (still works)
├── start_fullstack.sh         # Start both backend & frontend
├── run_backend.sh             # Start backend only
├── run_frontend.sh            # Start frontend only
└── SETUP.md                   # Detailed setup guide
```

## Available Interfaces

### Web Interface Features
- Modern chat-style interface
- Real-time responses
- Session-based conversations
- SQL query display
- Mobile-responsive design

### CLI Commands
- `quit` / `exit` / `q` - Exit interactive mode
- `refresh` - Reload database schema
- `generate-schema` - Generate new schema cache
- `test-connection` - Test database connectivity
- `schema-info` - Show cached schema information

### API Endpoints
- `POST /chat` - Send message to chatbot
- `GET /health` - Health check
- `GET /sessions/{id}/history` - Get chat history
- `POST /schema/refresh` - Refresh schema cache

## Installation

See [SETUP.md](SETUP.md) for detailed installation and setup instructions.