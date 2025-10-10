# Prompts to Insights - SMBC Risk Management Suite Setup

This guide will help you set up and run the complete application with CLI, web chat interface, and CCR Deck Assistant for chart analysis.

## Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL database
- OpenAI API key (GPT-4 access recommended for CCR analysis)
- PIL/Pillow for image processing
- python-pptx for PowerPoint generation

## Installation

### 1. Backend Setup (FastAPI)

```bash
# Navigate to project root
cd /var/www/html/SMBC/smbc_reporting_direct_sql

# Install Python dependencies (includes CCR functionality)
pip install -r backend/requirements.txt

# If you get import errors, install missing dependencies:
pip install python-multipart pillow python-pptx

# Configure environment variables
cp .env.example .env
# Edit .env with your database and OpenAI credentials
```

### 2. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies with legacy peer deps for compatibility
npm install --legacy-peer-deps

# Fix any security vulnerabilities (optional)
npm audit fix

# Build the application for production
npm run build

# Verify build was successful
ls -la build/
```

### 3. Environment Configuration

Create or update `.env` file in the project root:

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

# Admin Credentials (for demo)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 4. Frontend API Configuration (Optional)

Create `frontend/.env` file to customize API URLs. The system supports:

#### **Localhost (Default)**
```env
REACT_APP_MAIN_API_URL=http://localhost:8000
REACT_APP_CCR_API_URL=http://localhost:8001
```

#### **IP Addresses**
```env
# Same server, different ports
REACT_APP_MAIN_API_URL=http://192.168.1.100:8000
REACT_APP_CCR_API_URL=http://192.168.1.100:8001

# Different servers
REACT_APP_MAIN_API_URL=http://10.0.0.5:8000
REACT_APP_CCR_API_URL=http://10.0.0.6:8001
```

#### **Domain Names**
```env
# Production with domains
REACT_APP_MAIN_API_URL=https://api.company.com
REACT_APP_CCR_API_URL=https://ccr.company.com

# Mixed setup
REACT_APP_MAIN_API_URL=https://main-api.company.com:8000
REACT_APP_CCR_API_URL=http://192.168.1.50:8001
```

#### **Custom Ports**
```env
REACT_APP_MAIN_API_URL=http://192.168.1.100:9000
REACT_APP_CCR_API_URL=http://192.168.1.100:9001
```

## Running the Application

### Option 1: CLI Only

```bash
# From project root
python cli_app.py

# Or with a direct question
python cli_app.py "How many users are in the system?"

# Test connection
python cli_app.py test-connection

# Generate schema cache
python cli_app.py generate-schema
```

### Option 2: Web Interface

#### Start Backend API (Terminal 1)
```bash
# From project root
cd backend
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start CCR Backend (Terminal 2)
```bash
# From project root
cd smbc_reporting_tool
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Start Frontend (Terminal 3)
```bash
# From project root
cd frontend

# Option 1: Development server (auto-reload, debugging)
npm start

# Option 2: Production build and serve (faster, stable)
npm run build
npx serve -s build -l 3000

# Option 3: If port 3000 is busy, use different port
npx serve -s build -l 3001
```

The application will be available at:
- **Landing Page**: http://localhost:3000
- **Chat Interface**: http://localhost:3000/chat
- **CCR Deck Assistant**: http://localhost:3000/ccr
- **Admin Dashboard**: http://localhost:3000/admin
- **Main API**: http://localhost:8000
- **CCR API**: http://localhost:8001

## Admin Interface

The application includes an admin dashboard for managing user feedback and training data:

### Accessing Admin Interface
1. Start the full-stack application
2. Open http://localhost:3000
3. Click the **⚙️** (gear) icon on the home page
4. Login with admin credentials:
   - **Username**: admin
   - **Password**: admin123

### Admin Features
- **Feedback Management**: Review and approve/reject user feedback
- **Training Data**: View and manage approved training examples
- **Analytics**: Monitor user interactions and feedback trends

### Default Admin Credentials
- Username: `admin`
- Password: `admin123`

*Note: These are demo credentials. In production, implement proper authentication.*

### Option 3: Both CLI and Web

You can run both interfaces simultaneously:
- Use the web interface for interactive chat
- Use CLI for quick queries or automation

## API Endpoints

### Main Backend (Port 8000)
- `GET /health` - Health check
- `POST /chat` - Send message to chatbot
- `GET /sessions/{session_id}/history` - Get chat history
- `POST /schema/refresh` - Refresh database schema
- `POST /feedback` - Submit user feedback
- `POST /admin/login` - Admin authentication
- `GET /admin/feedbacks` - Get pending feedback
- `POST /admin/feedbacks/{id}/approve` - Approve feedback
- `GET /admin/training-data` - Get training data
- `GET /api/sample-data` - Get sample data for landing page

### CCR Backend (Port 8001)
- `POST /upload-images` - Upload chart images for analysis
- `POST /configure-cropping` - Configure image cropping settings
- `POST /analyze` - Analyze uploaded images with OpenAI GPT-4
- `GET /download-report` - Download PowerPoint report with analysis

## Features

### CLI Features
- Interactive question-answer mode
- Direct command-line queries
- Schema management
- Connection testing
- Executive report generation

### Pre-prompt Questions
The web interface includes quick-start cards for common queries:
- "Top 5 counterparties with highest credit exposure"
- "Top major movers in the last 3 months"
- "Key credit risk concentrations by MPE"

### Web Features
- **Professional Landing Page**: Feature showcase with navigation
- **Modern Chat Interface**: SMBC green branding with typing indicators
- **Pre-prompt Cards**: Quick-start questions for common counterparty risk queries
- **Expandable Results**: SQL query and raw data display
- **Feedback System**: Thumbs up/down voting with admin review
- **Executive PDF Reports**: Automated report generation
- **CCR Deck Assistant**: AI-powered chart analysis with configurable cropping
- **PowerPoint Generation**: Automated slide deck creation with insights
- **Admin Dashboard**: Feedback management and training data curation
- **React Router Navigation**: Clean URL structure (/chat, /ccr, /admin)
- **Session Management**: Multi-user support with chat history
- **Mobile-responsive Design**: Optimized for all devices

## Network Configuration

### Supported Configurations
- **Single Server**: Both APIs on same machine with different ports
- **Multiple Servers**: APIs distributed across different machines
- **Cloud Deployment**: APIs hosted on cloud services with public IPs
- **Docker**: Containerized deployment with custom networking
- **Load Balancer**: APIs behind load balancers with custom domains

### Configuration Examples by Scenario

#### **Development (Local)**
```env
REACT_APP_MAIN_API_URL=http://localhost:8000
REACT_APP_CCR_API_URL=http://localhost:8001
```

#### **LAN Deployment**
```env
REACT_APP_MAIN_API_URL=http://192.168.1.100:8000
REACT_APP_CCR_API_URL=http://192.168.1.100:8001
```

#### **Multi-Server Setup**
```env
REACT_APP_MAIN_API_URL=http://10.0.1.10:8000
REACT_APP_CCR_API_URL=http://10.0.1.20:8001
```

#### **Production with SSL**
```env
REACT_APP_MAIN_API_URL=https://api.smbc.com
REACT_APP_CCR_API_URL=https://ccr-api.smbc.com
```

## Troubleshooting

### Frontend Issues
```bash
# If localhost:3000 shows "connection refused":

# 1. Check if frontend is running
lsof -i :3000

# 2. Kill any existing processes on port 3000
kill -9 $(lsof -t -i:3000) 2>/dev/null || true

# 3. Clear npm cache and reinstall
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# 4. Build and serve the application
npm run build
npx serve -s build -l 3000

# 5. Alternative: Use development server
npm start
```

### Backend Issues
```bash
# Test database connection
python cli_app.py test-connection

# Check API health
curl http://localhost:8000/health

# View API logs
cd backend && python main.py
```

### Frontend Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check if backend is running
curl http://localhost:8000/health
```

### Common Issues

1. **Database Connection Failed**
   - Verify MySQL credentials in `.env`
   - Ensure MySQL server is running
   - Check network connectivity

2. **OpenAI API Errors**
   - Verify API key in `.env`
   - Check API quota and billing
   - Ensure internet connectivity

3. **CORS Errors**
   - Ensure backend is running on port 8000
   - Check frontend is running on port 3000
   - Verify CORS settings in `backend/main.py`

4. **Schema Cache Issues**
   - Delete `schema_cache.json` and regenerate
   - Run `python cli_app.py generate-schema`

5. **Admin Login Issues**
   - Verify admin credentials in environment variables
   - Check if admin endpoints are accessible
   - Clear browser cache and cookies

6. **Feedback System Issues**
   - Ensure database tables for feedback exist
   - Check feedback API endpoints are working
   - Verify admin interface can access feedback data

7. **Frontend Connection Refused (ERR_CONNECTION_REFUSED)**
   - Frontend not running: `cd frontend && npm start`
   - Port 3000 occupied: `kill -9 $(lsof -t -i:3000)` then restart
   - Build issues: `npm run build` then `npx serve -s build -l 3000`
   - Dependencies missing: `npm install --legacy-peer-deps`
   - Cache issues: `npm cache clean --force && rm -rf node_modules && npm install`

8. **Backend Import/Dependency Errors**
   - Missing python-multipart: `pip install python-multipart`
   - Missing PIL/Pillow: `pip install pillow`
   - Missing python-pptx: `pip install python-pptx`
   - Install all: `pip install -r backend/requirements.txt`
   - Virtual environment issues: `cd backend && python -m venv venv && source venv/bin/activate`

## Development

### Backend Development
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm start
```

### Adding New Features

1. **Backend**: Add endpoints in `backend/main.py`
2. **Frontend**: Add components in `frontend/src/components/`
3. **CLI**: Modify `cli_app.py` for new CLI features
4. **Core Logic**: Update `backend/chatbot_service.py` for shared functionality

## Production Deployment

### Docker (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build Docker image manually
docker build -t nl-to-sql-app .
docker run -p 8000:8000 --env-file .env nl-to-sql-app
```

### Manual Deployment

#### Backend
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend
```bash
cd frontend
npm run build

# Serve with nginx or apache
# Copy build/ contents to web server
```

## Architecture

```
├── backend/                 # FastAPI backend
│   ├── main.py             # API server
│   ├── chatbot_service.py  # Core chatbot logic
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   └── services/       # API services
│   └── package.json        # Node dependencies
├── src/                    # Original core modules
│   ├── core/              # Configuration
│   ├── services/          # Database, AI, Schema
│   └── utils/             # Console utilities
├── cli_app.py             # Updated CLI application
└── app.py                 # Original CLI (legacy)
```