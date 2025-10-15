# SMBC Risk Management Suite v1.0

A comprehensive full-stack application that converts natural language prompts into actionable insights by generating SQL queries and executing them against a MySQL database. Features integrated CCR Deck Assistant for chart analysis and PowerPoint report generation.

## 🚀 Features

- **Natural Language Processing**: Convert prompts to insights using OpenAI GPT-4
- **Safe Query Execution**: Execute queries with proper error handling and validation
- **Session Management**: Multi-user support with persistent chat history
- **CCR Deck Assistant**: Advanced chart analysis using GPT-4o vision capabilities
- **PowerPoint Generation**: Professional slide deck creation with SMBC corporate branding
- **Admin Dashboard**: Complete feedback management and training data curation system
- **Universal Compatibility**: Works with any domain/port combination

## 📋 Prerequisites

- **Python 3.8+** - [Download Python](https://python.org)
- **Node.js 16+** - [Download Node.js](https://nodejs.org)
- **MySQL Database** - Running and accessible
- **OpenAI API Key** - For AI-powered analysis

## ⚡ Quick Start

### Complete Setup (Recommended)
```bash
git clone https://github.com/SandeepIB/smbc_reporting_direct_sql.git
cd smbc_reporting_direct_sql

# Complete installation with domain setup
./install_with_domain.sh your-domain.com

# Configure environment
nano .env  # Update with your settings

# Start as background service
./manage_services.sh start
```

### Manual Setup
```bash
# 1. Install dependencies
./install.sh

# 2. Setup domain (optional)
./setup_domain.sh your-domain.com

# 3. Configure environment
nano .env

# 4. Start application
./start_fullstack.sh  # Development mode
# OR
./manage_services.sh start  # Background service
```

## 🔧 Configuration

Update `.env` file with your settings:
```env
OPENAI_API_KEY=your_openai_api_key_here
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

## 🛠️ Service Management

### Background Services (Production)
```bash
# Start services (survives terminal close)
./manage_services.sh start

# Stop services
./manage_services.sh stop

# Check status
./manage_services.sh status

# View logs
./manage_services.sh logs

# Remove services
./manage_services.sh remove
```

### Development Mode
```bash
# Interactive mode (stops when terminal closes)
./start_fullstack.sh
```

## 🌐 Domain Setup

### Automatic Web Server Installation
```bash
# Setup for production domain
./setup_domain.sh myapp.example.com

# Setup with SSL
sudo certbot --nginx -d your-domain.com
```

## 🎯 Usage

### Access Points
- **Web Interface**: http://localhost:3000 (or your domain)
- **Admin Panel**: Click ⚙️ icon (admin/admin123)

### Features
1. **Chat Interface**: Natural language to SQL queries
2. **CCR Deck Assistant**: Upload and analyze chart images
3. **Admin Dashboard**: Manage feedback and training data
4. **Executive Reports**: Generate professional reports

## 🔌 API Endpoints

- `POST /chat` - Send message to chatbot
- `GET /health` - Health check
- `POST /upload-images` - Upload chart images
- `POST /analyze` - Analyze uploaded images
- `GET /download-report` - Download PowerPoint report

## 🔍 Troubleshooting

### Common Issues
- **Backend won't start**: Check `backend/venv/` exists and `.env` is configured
- **Frontend build fails**: Run `cd frontend && npm install --legacy-peer-deps`
- **Database connection**: Verify MySQL is running and credentials are correct

### Logs
- **Service logs**: `./manage_services.sh logs`
- **Development logs**: Check terminal output
- **Browser logs**: F12 Developer Console

## 📚 Project Structure

```
├── backend/                 # FastAPI backend
├── frontend/                # React frontend
├── src/                     # Core modules
├── install.sh              # Install dependencies
├── start_fullstack.sh      # Development mode
├── manage_services.sh      # Service management
├── setup_domain.sh         # Domain configuration
└── install_with_domain.sh  # Complete setup
```

## 🤝 Support

1. Check this README for solutions
2. Review logs: `./manage_services.sh logs`
3. Verify prerequisites are installed
4. Ensure `.env` is configured correctly

## 📄 License

Proprietary software developed for SMBC risk management operations.