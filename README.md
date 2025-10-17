# SMBC Risk Management Suite v1.0

Full-stack application for natural language to SQL conversion with CCR Deck Assistant for chart analysis and PowerPoint generation.

## 🚀 Features

* **Natural Language to SQL**: OpenAI GPT-4 powered query generation
* **CCR Deck Assistant**: Chart analysis with PowerPoint report generation
* **Admin Dashboard**: Feedback management and training data curation
* **Universal Deployment**: Works with any domain/port combination

## 📋 Prerequisites

* **Python 3.8+** - [Download Python](https://python.org)
* **Node.js 16+** - [Download Node.js](https://nodejs.org)
* **MySQL Database** - Running and accessible
* **OpenAI API Key** - For AI-powered analysis

## ⚡ Quick Start

### Production Setup

```bash
git clone https://github.com/SandeepIB/smbc_reporting_direct_sql.git
cd smbc_reporting_direct_sql
./install.sh
./setup_production.sh your-domain.com
```

### Development Mode

```bash
./install.sh
./start_fullstack.sh
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

### Production Services (Background)

```bash
# Complete production setup
./setup_production.sh smbcaipoc.creatingwow.in

# Individual service control
./manage_services.sh start    # Start backend/frontend
./manage_services.sh stop     # Stop services
./manage_services.sh status   # Check status
./manage_services.sh logs     # View logs

# Proxy service control
sudo systemctl start smbc-proxy
sudo systemctl stop smbc-proxy
sudo systemctl status smbc-proxy
```

### Development Mode

```bash
./start_fullstack.sh  # Interactive mode (stops when terminal closes)
```

## 🌐 Domain Setup Guide

### Step 1: Basic Installation

```bash
git clone https://github.com/SandeepIB/smbc_reporting_direct_sql.git
cd smbc_reporting_direct_sql
./install.sh
```

### Step 2: Configure Environment

```bash
# Edit configuration file
nano .env

# Add your credentials:
OPENAI_API_KEY=your_key_here
MYSQL_HOST=localhost
MYSQL_USER=your_db_user
MYSQL_PASSWORD=your_db_password
MYSQL_DATABASE=your_database
```

### Step 3: Production Setup

```bash
# Setup with your domain
./setup_production.sh your-domain.com 8443
```

### Step 4: Domain Configuration

```bash
# Add domain to hosts file (for local testing)
echo "127.0.0.1 your-domain.com" | sudo tee -a /etc/hosts
```

### Step 5: Access Application

```bash
# Local access
https://your-domain.com:8443

# Admin panel: Click 🔧 icon
# Username: admin
# Password: admin123
```

## 🔍 Service Status & Troubleshooting

### Check All Services

```bash
sudo systemctl status smbc-backend smbc-frontend smbc-proxy
sudo journalctl -u smbc-backend -f
sudo journalctl -u smbc-frontend -f
sudo journalctl -u smbc-proxy -f
```

### Test Endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:3000
curl -k https://your-domain.com:8443/health
```

### Common Issues

**Services won't start**

```bash
./install.sh
cat .env
sudo systemctl restart smbc-backend smbc-frontend smbc-proxy
```

**Domain not accessible**

```bash
cat /etc/hosts | grep your-domain
sudo systemctl status smbc-proxy
ls -la your-domain.com.crt your-domain.com.key
```

**Database connection issues**

```bash
sudo systemctl status mysql
mysql -h localhost -u your_user -p your_database
```

## 🎯 Usage

### Access Points

* **Web Interface**: [https://your-domain.com:8443](https://your-domain.com:8443)
* **Admin Panel**: Click 🔧 icon (admin/admin123)
* **API Health**: [https://your-domain.com:8443/health](https://your-domain.com:8443/health)

### Features

1. **Chat Interface**: Natural language to SQL queries
2. **CCR Deck Assistant**: Upload and analyze chart images
3. **Admin Dashboard**: Manage feedback and training data
4. **Executive Reports**: Generate professional PowerPoint reports

## 📚 Project Structure

```
├── backend/                 # FastAPI backend
├── frontend/                # React frontend
├── src/                     # Core modules
├── install.sh               # Install dependencies
├── start_fullstack.sh       # Development mode
├── manage_services.sh       # Service management
├── setup_production.sh      # Production setup
└── README.md                # This file
```

## 🐜 API Endpoints

* `POST /chat` - Send message to chatbot
* `GET /health` - Health check
* `POST /upload-images` - Upload chart images
* `POST /analyze` - Analyze uploaded images
* `GET /download-report` - Download PowerPoint report

## 🤝 Support

1. Check service status: `sudo systemctl status smbc-*`
2. Review logs: `sudo journalctl -u smbc-backend -f`
3. Verify configuration: `cat .env`
4. Test endpoints: `curl -k https://your-domain.com:8443/health`

## 📜 Fine-Tune Model Training

The application supports fine-tuning an OpenAI model to improve SQL query generation based on your own training data.

### 1️⃣ Prepare Environment

```bash
cd smbc_reporting_direct_sql
source backend/venv/bin/activate
```

Ensure `.env` has:

```env
OPENAI_API_KEY=your_openai_api_key_here
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

### 2️⃣ Generate Schema Cache

```bash
python -m src.services.schema_cache
```

### 3️⃣ Export Training Data & Start Fine-Tune

```bash
python -m src.services.train_finetune_model
```

### 4️⃣ Check Fine-Tune Status (CLI)

```bash
export $(grep OPENAI_API_KEY .env)
openai api fine_tuning.jobs.list
openai api fine_tuning.jobs.retrieve -i YOUR_JOB_ID
```

### 5️⃣ Update AIService

Once fine-tuning completes, update `.env`:

```env
FINETUNED_MODEL=your_finetuned_model_name
```

### 6️⃣ Optional: Watch Job Continuously

```bash
watch -n 10 "openai api fine_tuning.jobs.retrieve -i YOUR_JOB_ID"
```

### 7️⃣ Tips

* Only approved data (`approved_by`) is exported.
* Do not change the `training_data` table structure.
* Adjust `ROW_LIMIT` in `.env` for larger datasets.

## 👍 License

Proprietary software developed for SMBC risk management operations.
