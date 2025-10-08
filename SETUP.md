# Full-Stack Counterparty Risk Assistant Application Setup

This guide will help you set up and run the complete application with both CLI and web interfaces.

## Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL database
- OpenAI API key

## Installation

### 1. Backend Setup (FastAPI)

```bash
# Navigate to project root
cd /var/www/html/approch2-direct-sql

# Install Python dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database and OpenAI credentials
```

### 2. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
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

#### Start Frontend (Terminal 2)
```bash
# From project root
cd frontend
npm start
```

The web interface will be available at: http://localhost:3000
The API will be available at: http://localhost:8000
The admin interface will be available at: http://localhost:3000 (click gear icon)

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
- Modern chat interface with SMBC green branding
- Pre-prompt cards for common counterparty risk questions
- Expandable results section showing SQL query and raw data
- Feedback system with thumbs up/down voting
- Executive PDF report generation
- Admin dashboard for feedback management
- Session-based conversations
- Real-time responses with typing indicators
- Mobile-responsive design

## Troubleshooting

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