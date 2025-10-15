#!/bin/bash

# SMBC Service Management Script

set -e

PROJECT_DIR=$(pwd)
USER=$(whoami)

case "${1:-help}" in
    "create")
        echo "🔧 Creating SMBC systemd services..."
        
        # Backend service
        sudo tee /etc/systemd/system/smbc-backend.service > /dev/null <<EOF
[Unit]
Description=SMBC Risk Management Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$PROJECT_DIR/backend/venv/bin
ExecStart=$PROJECT_DIR/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        # Frontend service
        sudo tee /etc/systemd/system/smbc-frontend.service > /dev/null <<EOF
[Unit]
Description=SMBC Risk Management Frontend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/frontend
Environment=NODE_ENV=production
Environment=GENERATE_SOURCEMAP=false
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable smbc-backend smbc-frontend
        echo "✅ Services created and enabled"
        ;;
        
    "start")
        echo "🚀 Starting SMBC services..."
        
        # Create services if they don't exist
        if ! systemctl list-unit-files | grep -q smbc-backend.service; then
            $0 create
        fi
        
        # Stop existing processes
        pkill -f "python.*main.py" 2>/dev/null || true
        pkill -f "node.*3000" 2>/dev/null || true
        lsof -ti:3000,8000 | xargs kill -9 2>/dev/null || true
        
        sudo systemctl start smbc-backend smbc-frontend
        sleep 2
        
        echo "📊 Status:"
        sudo systemctl is-active smbc-backend && echo "✅ Backend: Running" || echo "❌ Backend: Failed"
        sudo systemctl is-active smbc-frontend && echo "✅ Frontend: Running" || echo "❌ Frontend: Failed"
        echo ""
        echo "🌐 Access: http://localhost:3000"
        echo "📋 Logs: sudo journalctl -u smbc-backend -f"
        ;;
        
    "stop")
        echo "🛑 Stopping SMBC services..."
        sudo systemctl stop smbc-backend smbc-frontend 2>/dev/null || true
        pkill -f "python.*main.py" 2>/dev/null || true
        pkill -f "node.*3000" 2>/dev/null || true
        echo "✅ Services stopped"
        ;;
        
    "status")
        echo "📊 SMBC Service Status:"
        sudo systemctl status smbc-backend smbc-frontend --no-pager
        ;;
        
    "logs")
        echo "📋 SMBC Service Logs (Ctrl+C to exit):"
        sudo journalctl -u smbc-backend -u smbc-frontend -f
        ;;
        
    "remove")
        echo "🗑️ Removing SMBC services..."
        sudo systemctl stop smbc-backend smbc-frontend 2>/dev/null || true
        sudo systemctl disable smbc-backend smbc-frontend 2>/dev/null || true
        sudo rm -f /etc/systemd/system/smbc-*.service
        sudo systemctl daemon-reload
        echo "✅ Services removed"
        ;;
        
    *)
        echo "SMBC Service Management"
        echo ""
        echo "Usage: $0 {create|start|stop|status|logs|remove}"
        echo ""
        echo "Commands:"
        echo "  create  - Create systemd services"
        echo "  start   - Start services (survives terminal close)"
        echo "  stop    - Stop services"
        echo "  status  - Check service status"
        echo "  logs    - View service logs"
        echo "  remove  - Remove services completely"
        ;;
esac