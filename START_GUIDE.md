# Application Startup Guide

## ✅ **FIXED: Startup Scripts Now Working**

### **Option 1: Full Application (Recommended)**
```bash
bash start_fullstack.sh
```
- Starts both backend API (port 8000) and frontend React app (port 3000)
- Automatically creates virtual environment and installs dependencies
- Access at: http://localhost:3000

### **Option 2: Backend Only**
```bash
bash start_backend_only.sh
```
- Starts only the backend API server
- Useful for testing API endpoints or using CLI
- Access at: http://localhost:8000
- API docs at: http://localhost:8000/docs

### **Option 3: CLI Interface**
```bash
python cli_app.py
```
- Command-line interface for direct queries
- No web interface needed

## **Admin Access**
1. Start application: `bash start_fullstack.sh`
2. Open: http://localhost:3000
3. Click ⚙️ (gear icon) on home page
4. Login: `admin` / `admin123`
5. Access admin dashboard with:
   - Pending feedback management
   - All feedback CRUD operations
   - Training data management
   - Add new training data

## **What Was Fixed**
- ✅ Virtual environment creation
- ✅ Automatic dependency installation
- ✅ Proper uvicorn execution
- ✅ MySQL connector dependency added
- ✅ Error handling and cleanup

## **Requirements**
- Python 3.7+
- Node.js 14+ (for frontend)
- MySQL database
- OpenAI API key in .env file

## **Troubleshooting**
- If frontend fails: Use `bash start_backend_only.sh` and access API directly
- If database connection fails: Check .env file credentials
- If port conflicts: Scripts automatically find available ports