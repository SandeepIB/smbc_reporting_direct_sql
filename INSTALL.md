# Installation Guide - SMBC Risk Management Suite

## Quick Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- OpenAI API Key

### 1. Backend Setup
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install missing dependencies if needed
pip install python-multipart pillow python-pptx
```

### 2. Frontend Setup
```bash
# Complete setup with security fixes
./setup_frontend.sh

# Or manual setup
cd frontend
npm install --legacy-peer-deps
npm audit fix
npm run build
```

### 3. Environment Configuration
Create `.env` file:
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

### 4. Start Application
```bash
# Start full-stack application
./start_fullstack.sh

# Or start services individually
./run_backend.sh    # Backend on port 8000
./run_frontend.sh   # Frontend on port 3000
```

## Access Points
- **Main Application**: http://localhost:3000
- **Chat Interface**: http://localhost:3000/chat
- **CCR Deck Assistant**: http://localhost:3000/ccr
- **Admin Dashboard**: http://localhost:3000/admin
- **API Documentation**: http://localhost:8000/docs

## Features Verification

### CCR Deck Assistant
1. Navigate to http://localhost:3000/ccr
2. Upload chart images
3. Enable "Automatic image cropping" checkbox
4. Click "Analyze Charts"
5. Verify PowerPoint-style results with thumbnails

### Image Cropping Test
- Upload image → Enable cropping → Analyze
- Should create 6 cropped segments (2x3 grid)
- Each segment analyzed individually
- Results displayed with chart thumbnails

## Troubleshooting

### Frontend Issues
```bash
# Debug frontend connections
./debug_frontend.sh

# Production build
./start_frontend_production.sh
```

### Backend Dependencies
```bash
# Fix missing dependencies
./fix_backend_dependencies.sh
```

### Common Issues
- **OpenAI Quota**: Check billing at https://platform.openai.com/usage
- **Port Conflicts**: Ensure ports 3000 and 8000 are available
- **Cache Issues**: Hard refresh browser (Ctrl+F5)

## Architecture
- **Unified Backend**: Single service on port 8000
- **React Frontend**: Development server on port 3000
- **Database**: MySQL with org_insights schema
- **Image Processing**: PIL for cropping, OpenAI GPT-4o for analysis