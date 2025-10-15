#!/bin/bash

# SMBC Domain Setup Script with Web Server Auto-Install

set -e

DOMAIN=${1:-"localhost"}
PORT=${2:-"80"}
SSL_PORT=${3:-"443"}

echo "🚀 Setting up SMBC Risk Management Suite for domain: $DOMAIN"

# Function to detect OS
detect_os() {
    if [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/redhat-release ]; then
        echo "redhat"
    else
        echo "unknown"
    fi
}

# Function to install nginx
install_nginx() {
    echo "📦 Installing nginx..."
    OS=$(detect_os)
    
    case $OS in
        "debian")
            sudo apt update
            sudo apt install -y nginx
            ;;
        "redhat")
            sudo yum install -y epel-release
            sudo yum install -y nginx
            ;;
        *)
            echo "❌ Unsupported OS. Please install nginx manually."
            exit 1
            ;;
    esac
    
    sudo systemctl enable nginx
    sudo systemctl start nginx
    echo "✅ Nginx installed and started"
}

# Function to install apache2
install_apache() {
    echo "📦 Installing Apache2..."
    OS=$(detect_os)
    
    case $OS in
        "debian")
            sudo apt update
            sudo apt install -y apache2
            sudo a2enmod proxy
            sudo a2enmod proxy_http
            sudo a2enmod ssl
            ;;
        "redhat")
            sudo yum install -y httpd
            ;;
        *)
            echo "❌ Unsupported OS. Please install Apache manually."
            exit 1
            ;;
    esac
    
    sudo systemctl enable apache2 2>/dev/null || sudo systemctl enable httpd
    sudo systemctl start apache2 2>/dev/null || sudo systemctl start httpd
    echo "✅ Apache installed and started"
}

# Check for web server
check_webserver() {
    if command -v nginx >/dev/null 2>&1; then
        echo "✅ Nginx found"
        return 0
    elif command -v apache2 >/dev/null 2>&1 || command -v httpd >/dev/null 2>&1; then
        echo "✅ Apache found"
        return 1
    else
        echo "❌ No web server found"
        return 2
    fi
}

# Create nginx config
create_nginx_config() {
    sudo tee /etc/nginx/sites-available/smbc > /dev/null <<EOF
server {
    listen $PORT;
    server_name $DOMAIN;
    
    # Frontend (React)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Backend endpoints
    location ~ ^/(chat|health|admin|feedback|templates|upload-images|configure-cropping|analyze|download-report|get-image|sample-data|confirm|refine|generate-report|schema|process-feedback|sessions|select-template)\$ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/smbc /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    echo "✅ Nginx configured for $DOMAIN"
}

# Create apache config
create_apache_config() {
    sudo tee /etc/apache2/sites-available/smbc.conf > /dev/null <<EOF
<VirtualHost *:$PORT>
    ServerName $DOMAIN
    
    # Frontend (React)
    ProxyPreserveHost On
    ProxyPass /api/ http://localhost:8000/
    ProxyPassReverse /api/ http://localhost:8000/
    
    # Backend endpoints
    ProxyPass /chat http://localhost:8000/chat
    ProxyPass /health http://localhost:8000/health
    ProxyPass /admin http://localhost:8000/admin
    ProxyPass /feedback http://localhost:8000/feedback
    ProxyPass /templates http://localhost:8000/templates
    ProxyPass /upload-images http://localhost:8000/upload-images
    ProxyPass /configure-cropping http://localhost:8000/configure-cropping
    ProxyPass /analyze http://localhost:8000/analyze
    ProxyPass /download-report http://localhost:8000/download-report
    ProxyPass /get-image http://localhost:8000/get-image
    ProxyPass /sample-data http://localhost:8000/sample-data
    ProxyPass /confirm http://localhost:8000/confirm
    ProxyPass /refine http://localhost:8000/refine
    ProxyPass /generate-report http://localhost:8000/generate-report
    ProxyPass /schema http://localhost:8000/schema
    ProxyPass /process-feedback http://localhost:8000/process-feedback
    ProxyPass /sessions http://localhost:8000/sessions
    ProxyPass /select-template http://localhost:8000/select-template
    
    # Everything else to frontend
    ProxyPass / http://localhost:3000/
    ProxyPassReverse / http://localhost:3000/
</VirtualHost>
EOF

    sudo a2ensite smbc.conf
    sudo systemctl reload apache2 2>/dev/null || sudo systemctl reload httpd
    echo "✅ Apache configured for $DOMAIN"
}

# Main execution
main() {
    echo "🔍 Checking for web server..."
    
    check_webserver
    WEBSERVER_STATUS=$?
    
    case $WEBSERVER_STATUS in
        0)  # Nginx found
            echo "📝 Configuring Nginx..."
            create_nginx_config
            ;;
        1)  # Apache found
            echo "📝 Configuring Apache..."
            create_apache_config
            ;;
        2)  # No web server found
            echo "❓ Which web server would you like to install?"
            echo "1) Nginx (recommended)"
            echo "2) Apache2"
            read -p "Enter choice (1 or 2): " choice
            
            case $choice in
                1)
                    install_nginx
                    create_nginx_config
                    ;;
                2)
                    install_apache
                    create_apache_config
                    ;;
                *)
                    echo "❌ Invalid choice. Exiting."
                    exit 1
                    ;;
            esac
            ;;
    esac
    
    echo ""
    echo "🎉 Domain setup complete!"
    echo "📍 Domain: $DOMAIN:$PORT"
    echo "🔧 Frontend: http://localhost:3000 (proxied)"
    echo "🔧 Backend: http://localhost:8000 (proxied)"
    echo ""
    echo "📋 Next steps:"
    echo "1. Start the application: ./start_fullstack.sh"
    echo "2. Access via: http://$DOMAIN:$PORT"
    echo ""
    echo "💡 To enable SSL, run: sudo certbot --nginx -d $DOMAIN"
}

# Check if running as root for certain operations
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Running as root. Some operations may not require sudo."
fi

main "$@"