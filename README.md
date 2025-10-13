# Prompts to Insights - SMBC Risk Management Suite

A comprehensive full-stack application that converts natural language prompts into actionable insights by generating SQL queries and executing them against a MySQL database. Features integrated CCR Deck Assistant for chart analysis and PowerPoint report generation.

## Features

### Core Features
- **Cacheable Schema Generation**: Generate database schema once and reuse
- **Natural Language Processing**: Convert prompts to insights using OpenAI GPT-4
- **Safe Query Execution**: Execute queries with proper error handling
- **Session Management**: Multi-user support with chat history
- **Pre-prompt Cards**: Quick-start questions for common counterparty risk queries
- **Feedback System**: Thumbs up/down voting with admin review interface and training data curation
- **Executive Reports**: PDF report generation with query results and insights
- **CCR Deck Assistant**: AI-powered chart analysis with PowerPoint report generation
- **Professional Landing Page**: Modern interface with feature showcase and navigation

### Enhanced CCR Features
- **Automatic Image Cropping**: Split charts into 2x3 grid for detailed analysis
- **PowerPoint-Style Layout**: Preview results with thumbnails and professional formatting
- **Cancel Analysis**: Stop analysis mid-process with AbortController
- **Unified Backend**: Single-port architecture for simplified deployment
- **Mobile-Responsive Design**: Optimized for desktop and mobile devices

### Interface Options
- **Web Interface**: Modern React-based interface with SMBC branding and routing
- **CLI Interface**: Interactive command-line tool
- **REST API**: FastAPI backend for integration
- **Admin Dashboard**: Feedback management and training data curation
- **CCR Analysis Tool**: Dedicated interface for chart image analysis

## Setup

1. Install backend dependencies:
```bash
pip install -r backend/requirements.txt

# Or install specific missing dependencies:
pip install python-multipart pillow python-pptx
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

# Build the application (required for production)
npm run build
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

3. Configure frontend API URLs in `frontend/.env` (optional):
```env
# Frontend API Configuration (defaults to localhost if not set)
REACT_APP_MAIN_API_URL=http://localhost:8000
REACT_APP_CCR_API_URL=http://localhost:8001

# Examples with IP addresses:
# REACT_APP_MAIN_API_URL=http://192.168.1.100:8000
# REACT_APP_CCR_API_URL=http://192.168.1.100:8001

# Examples with different server IPs:
# REACT_APP_MAIN_API_URL=http://10.0.0.5:8000
# REACT_APP_CCR_API_URL=http://10.0.0.6:8001

# Examples with domain names:
# REACT_APP_MAIN_API_URL=https://api.company.com
# REACT_APP_CCR_API_URL=https://ccr.company.com
```

## Quick Start

### 1. Install Dependencies
```bash
# Run the installation script
./install.sh
```

### 2. Configure Environment
Update `.env` file with your settings:
```env
OPENAI_API_KEY=your_openai_api_key
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

### 3. Start Application
```bash
# Start the full application
./start_fullstack.sh
```

### 4. Access Application
- **Web Interface**: http://localhost:3000
- **API Server**: http://localhost:8000
- **Admin Panel**: http://localhost:3000 (click ⚙️ icon)

**Admin Credentials**: admin / admin123

## Alternative Start Methods

### CLI Only
```bash
python cli_app.py
```

### Backend Only
```bash
./run_backend.sh
```

### Frontend Only
```bash
./run_frontend.sh
```

## File Structure

```
├── backend/                    # FastAPI backend
│   ├── main.py                # API server
│   ├── chatbot_service.py     # Core chatbot logic
│   ├── feedback_service.py    # Feedback management
│   └── requirements.txt       # Backend dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── LandingPage.js # Landing page
│   │   │   ├── ChatInterface.js # Chat interface
│   │   │   ├── AdminPage.js   # Admin dashboard
│   │   │   └── FeedbackSection.js # Feedback system
│   │   └── services/          # API services
│   └── package.json           # Frontend dependencies
├── src/                       # Core modules
│   ├── core/                  # Configuration
│   ├── services/              # Database, AI, Schema services
│   └── utils/                 # Utilities
├── cli_app.py                 # CLI application
├── install.sh                 # Installation script
├── start_fullstack.sh         # Start application
├── run_backend.sh             # Start backend only
├── run_frontend.sh            # Start frontend only
└── README.md                  # This file
```

## Configuration Options

### Backend URL Configuration
The application supports flexible backend configuration through environment variables:

- **Localhost** (default): `http://localhost:8000` and `http://localhost:8001`
- **IP Addresses**: `http://192.168.1.100:8000` and `http://192.168.1.100:8001`
- **Domain Names**: `https://api.company.com` and `https://ccr.company.com`
- **Mixed Setup**: Different IPs/domains for each service
- **Different Ports**: Customize ports as needed

No code changes required - only update `frontend/.env` file.

## Available Interfaces

### Web Interface Features
- **Professional Landing Page**: Feature showcase with navigation and SMBC branding
- **Chat Interface**: Modern chat-style interface with SMBC green theme
- **Real-time Responses**: Typing indicators and session-based conversations
- **SQL Query Display**: Expandable SQL query and raw data display
- **Pre-prompt Cards**: Quick-start questions for common counterparty risk queries
- **Feedback System**: Thumbs up/down voting with admin review interface
- **Executive PDF Reports**: Automated report generation with query results
- **CCR Deck Assistant**: AI-powered chart analysis with configurable cropping
- **PowerPoint Generation**: Automated slide deck creation with analysis insights
- **Mobile-responsive Design**: Optimized for desktop and mobile devices
- **Admin Dashboard**: Feedback management and training data curation
- **React Router Navigation**: Clean URL structure with proper routing

### CCR Analysis Features
- **Smart Image Cropping**: Automatically split charts into 6 segments (2x3 grid)
- **Individual Block Analysis**: Each cropped section analyzed separately by GPT-4o
- **PowerPoint Preview**: Results displayed in presentation-style layout
- **Chart Thumbnails**: Visual preview of analyzed image segments
- **Professional Formatting**: Clean, structured analysis with trend and recommendation sections
- **Cancel Functionality**: Stop analysis process at any time
- **Error Handling**: Comprehensive error messages and retry mechanisms

### CLI Commands
- `quit` / `exit` / `q` - Exit interactive mode
- `refresh` - Reload database schema
- `generate-schema` - Generate new schema cache
- `test-connection` - Test database connectivity
- `schema-info` - Show cached schema information

### API Endpoints

#### Unified Backend (Port 8000)
**Main API Endpoints:**
- `POST /chat` - Send message to chatbot
- `GET /health` - Health check
- `GET /sessions/{id}/history` - Get chat history
- `POST /schema/refresh` - Refresh schema cache
- `POST /feedback` - Submit user feedback
- `POST /admin/login` - Admin authentication
- `GET /admin/feedbacks` - Get pending feedback
- `POST /admin/feedbacks/{id}/approve` - Approve feedback
- `GET /admin/training-data` - Get training data
- `GET /api/sample-data` - Get sample data for landing page

**CCR Analysis Endpoints:**
- `POST /upload-images` - Upload chart images for analysis
- `POST /configure-cropping` - Configure image cropping settings (2x3 grid)
- `POST /analyze` - Analyze uploaded images with AI (supports cropping)
- `GET /download-report` - Download PowerPoint report with analysis

## Installation

See [SETUP.md](SETUP.md) for detailed installation and setup instructions.