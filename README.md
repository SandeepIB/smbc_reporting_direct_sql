# SMBC Risk Management Suite

A comprehensive full-stack application that converts natural language prompts into actionable insights by generating SQL queries and executing them against a MySQL database. Features integrated CCR Deck Assistant for chart analysis and PowerPoint report generation.

## 🚀 Features

### Core Features
- **Natural Language Processing**: Convert prompts to insights using OpenAI GPT-4
- **Safe Query Execution**: Execute queries with proper error handling
- **Session Management**: Multi-user support with chat history
- **Pre-prompt Cards**: Quick-start questions for common counterparty risk queries
- **Feedback System**: Thumbs up/down voting with admin review interface
- **Executive Reports**: PDF report generation with query results and insights

### CCR Deck Assistant
- **AI-Powered Chart Analysis**: Analyze chart images using GPT-4o
- **Image Cropping**: Automatically split charts into 2x3 grid for detailed analysis
- **PowerPoint Generation**: Professional slide deck creation with SMBC branding
- **Image Thumbnails**: View actual chart images with zoom functionality
- **Edit Capabilities**: Common edit mode for all analysis results
- **Professional Layout**: Image thumbnails on left, analysis content on right

### Interface Options
- **Web Interface**: Modern React-based interface with SMBC branding
- **CLI Interface**: Interactive command-line tool
- **REST API**: FastAPI backend for integration
- **Admin Dashboard**: Feedback management and training data curation

## 📋 Prerequisites

- **Python 3.8+** - [Download Python](https://python.org)
- **Node.js 16+** - [Download Node.js](https://nodejs.org)
- **MySQL Database** - Running and accessible
- **OpenAI API Key** - For AI-powered analysis

## ⚡ Quick Start

### Option 1: Complete Setup with Domain (Recommended)
```bash
git clone https://github.com/SandeepIB/smbc_reporting_direct_sql.git
cd smbc_reporting_direct_sql

# Complete installation with domain setup
./install_with_domain.sh your-domain.com

# Configure environment
# Update .env file with your settings

# Start application
./start_fullstack.sh
```

### Option 2: Manual Setup
```bash
# 1. Clone Repository
git clone https://github.com/SandeepIB/smbc_reporting_direct_sql.git
cd smbc_reporting_direct_sql

# 2. Install Dependencies
./install.sh

# 3. Setup Domain (Optional)
./setup_domain.sh your-domain.com

# 4. Configure Environment
# Update .env file with your settings

# 5. Start Application
./start_fullstack.sh
```

### Environment Configuration
Update `.env` file with your settings:
```env
OPENAI_API_KEY=your_openai_api_key_here
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

### Access Points
- **Web Interface**: http://your-domain.com (or http://localhost:3000)
- **API Server**: http://localhost:8000 (proxied through web server)
- **Admin Panel**: Click ⚙️ icon in web interface

**Admin Credentials**: admin / admin123

## 🏗️ Architecture

```
├── backend/                    # FastAPI backend
│   ├── main.py                # API server with unified endpoints
│   ├── ccr_endpoints.py       # CCR analysis functionality
│   ├── chatbot_service.py     # Core chatbot logic
│   ├── feedback_service.py    # Feedback management
│   ├── requirements.txt       # Backend dependencies
│   └── SMBC.pptx             # PowerPoint template
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── LandingPage.js # Landing page
│   │   │   ├── ChatInterface.js # Chat interface
│   │   │   ├── CCRDeckAssistantPage.js # CCR analysis
│   │   │   ├── CommonHeader.js # Navigation header
│   │   │   └── AdminPage.js   # Admin dashboard
│   │   └── config/api.js      # API configuration
│   └── package.json           # Frontend dependencies
├── src/                       # Core modules
│   ├── core/config.py         # Configuration management
│   ├── services/              # Database, AI, Schema services
│   └── utils/                 # Utilities
├── install.sh                 # Installation script
├── start_fullstack.sh         # Application startup
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```env
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
```

### Frontend Configuration (frontend/.env)
```env
# API URLs (optional - defaults to localhost)
REACT_APP_API_URL=http://localhost:8000
```

## 🎯 Usage

### Chat Interface
1. Navigate to http://localhost:3000
2. Click "Start Chat" to begin
3. Ask natural language questions about your data
4. Review generated SQL and results
5. Download executive reports as needed

### CCR Deck Assistant
1. Navigate to http://localhost:3000/ccr
2. Upload chart images (PNG, JPG, JPEG)
3. Configure analysis settings (cropping optional)
4. Click "Analyze Charts" to process
5. Review insights and edit if needed
6. Download professional PowerPoint report

### Admin Dashboard
1. Click the ⚙️ icon in the top navigation
2. Login with admin/admin123
3. Review user feedback
4. Manage training data
5. Approve/reject feedback submissions

## 🔌 API Endpoints

### Main API (Port 8000)
- `POST /chat` - Send message to chatbot
- `GET /health` - Health check
- `POST /feedback` - Submit user feedback
- `POST /admin/login` - Admin authentication

### CCR Analysis
- `POST /upload-images` - Upload chart images
- `POST /configure-cropping` - Configure image cropping
- `POST /analyze` - Analyze uploaded images
- `GET /download-report` - Download PowerPoint report
- `GET /get-image/{filename}` - Serve image files

## 🌐 Domain Setup

### Automatic Web Server Installation
The `setup_domain.sh` script automatically:
- **Detects** existing web servers (Nginx/Apache)
- **Installs** web server if none found
- **Configures** reverse proxy for your domain
- **Sets up** SSL-ready configuration

### Usage Examples
```bash
# Setup for production domain
./setup_domain.sh myapp.example.com

# Setup for local development
./setup_domain.sh localhost 8080

# Setup with custom ports
./setup_domain.sh myapp.com 80 443
```

### SSL Certificate (Optional)
```bash
# Install certbot and get SSL certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🛠️ Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm start
```

### CLI Interface
```bash
python cli_app.py
```

## 🔍 Troubleshooting

### Common Issues

**Backend won't start**
- Check if virtual environment exists: `backend/venv/`
- Verify Python dependencies: `pip list`
- Check database connection in `.env`

**Frontend build fails**
- Clear node_modules: `rm -rf frontend/node_modules`
- Reinstall: `cd frontend && npm install --legacy-peer-deps`

**CCR Analysis not working**
- Verify OpenAI API key in `.env`
- Check image file formats (PNG, JPG, JPEG only)
- Ensure backend is running on port 8000

**Database connection issues**
- Verify MySQL is running
- Check credentials in `.env`
- Test connection manually

### Logs and Debugging
- Backend logs: Check terminal output where uvicorn is running
- Frontend logs: Check browser developer console (F12)
- Network issues: Check browser Network tab for failed requests

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://reactjs.org/docs)
- [MySQL Documentation](https://dev.mysql.com/doc)

## 🤝 Support

For issues and questions:
1. Check this README for common solutions
2. Review error logs in terminal/browser console
3. Verify all prerequisites are installed
4. Ensure `.env` configuration is correct

## 📄 License

This project is proprietary software developed for SMBC risk management operations.