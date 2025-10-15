#!/bin/bash

# SMBC Production Setup Script

set -e

DOMAIN=${1:-"localhost"}
PORT=${2:-"8443"}

echo "🚀 SMBC Production Setup for $DOMAIN"

# Function to create HTTPS proxy
create_https_proxy() {
    cat > https_proxy.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import ssl
import os
import sys

class SMBCProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            # Route API requests to backend, everything else to frontend
            if any(self.path.startswith(p) for p in ['/api/', '/health', '/chat', '/admin/', '/feedback', '/templates', '/upload-images', '/configure-cropping', '/analyze', '/download-report', '/get-image/', '/sample-data', '/confirm', '/refine', '/generate-report', '/schema/', '/process-feedback', '/sessions/', '/select-template']):
                url = f"http://localhost:8000{self.path}"
            else:
                url = f"http://localhost:3000{self.path}"
            
            # Handle POST data
            post_data = None
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            req = urllib.request.Request(url, data=post_data, method=self.command)
            
            # Copy headers
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection', 'content-length']:
                    req.add_header(header, value)
            
            with urllib.request.urlopen(req) as response:
                self.send_response(response.getcode())
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.read())
                
        except Exception as e:
            self.send_error(502, f"Proxy Error: {e}")

def main():
    domain = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8443
    
    print(f"🚀 Starting HTTPS proxy for {domain} on port {port}")
    
    httpd = socketserver.TCPServer(("", port), SMBCProxyHandler)
    
    # Setup SSL
    cert_file = f"{domain}.crt"
    key_file = f"{domain}.key"
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        protocol = "https"
    else:
        protocol = "http"
    
    print(f"🌐 Access: {protocol}://{domain}:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Proxy stopped")

if __name__ == "__main__":
    main()
EOF
    chmod +x https_proxy.py
}

# Function to generate SSL certificate
generate_ssl() {
    if [ ! -f "$DOMAIN.crt" ]; then
        echo "🔐 Generating SSL certificate for $DOMAIN..."
        openssl req -x509 -newkey rsa:4096 -keyout "$DOMAIN.key" -out "$DOMAIN.crt" -days 365 -nodes -subj "/C=US/ST=State/L=City/O=SMBC/CN=$DOMAIN" 2>/dev/null
        echo "✅ SSL certificate generated"
    fi
}

# Function to create systemd service for proxy
create_proxy_service() {
    sudo tee /etc/systemd/system/smbc-proxy.service > /dev/null <<EOF
[Unit]
Description=SMBC HTTPS Proxy
After=network.target smbc-backend.service smbc-frontend.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/https_proxy.py $DOMAIN $PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable smbc-proxy.service
    echo "✅ Proxy service created"
}

# Main setup
echo "📦 Step 1: Creating HTTPS proxy..."
create_https_proxy

echo "🔐 Step 2: Generating SSL certificate..."
generate_ssl

echo "🔧 Step 3: Creating services..."
./manage_services.sh create

echo "🌐 Step 4: Creating proxy service..."
create_proxy_service

echo "▶️  Step 5: Starting all services..."
sudo systemctl start smbc-backend smbc-frontend smbc-proxy

echo ""
echo "🎉 Production setup complete!"
echo ""
echo "🌐 Access URLs:"
echo "   HTTPS: https://$DOMAIN:$PORT"
echo "   Local: http://localhost:3000"
echo ""
echo "📋 Add to /etc/hosts:"
echo "   127.0.0.1 $DOMAIN"
echo ""
echo "🔧 Service Management:"
echo "   Status: sudo systemctl status smbc-backend smbc-frontend smbc-proxy"
echo "   Logs: sudo journalctl -u smbc-proxy -f"
echo "   Stop: sudo systemctl stop smbc-backend smbc-frontend smbc-proxy"