#!/bin/bash

DOMAIN=${1:-"aipoc.creatingwow.in"}
PORT=${2:-9443}

echo "=== Quick HTTPS Setup ==="
echo "Domain: $DOMAIN | HTTPS Port: $PORT | Backends: localhost:3000 & localhost:8000"

# Kill existing processes
pkill -f python3.*https 2>/dev/null

# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "$DOMAIN.key" -out "$DOMAIN.crt" -subj "/CN=$DOMAIN" 2>/dev/null

# Create HTTPS server
python3 -c "
import http.server, socketserver, urllib.request, ssl, sys

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Route based on path or try both backends
            backend_port = 8000 if '/api/' in self.path else 3000
            url = f'http://localhost:{backend_port}{self.path}'
            with urllib.request.urlopen(url) as response:
                self.send_response(response.getcode())
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.read())
        except:
            self.send_error(502, 'Backend Error')
    
    def do_POST(self): self.do_GET()

httpd = socketserver.TCPServer(('', $PORT), ProxyHandler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('$DOMAIN.crt', '$DOMAIN.key')
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
print(f'HTTPS server: https://$DOMAIN:$PORT')
httpd.serve_forever()
" &

sleep 2

# Open browser
#google-chrome --ignore-certificate-errors --allow-running-insecure-content --user-data-dir=/tmp/chrome_dev "https://$DOMAIN:$PORT" > /dev/null 2>&1 &

echo "✅ Server running at https://$DOMAIN:$PORT"
echo "🔄 Proxying: /api/* → localhost:8000, others → localhost:3000"
echo "📝 Type 'thisisunsafe' on SSL warning"