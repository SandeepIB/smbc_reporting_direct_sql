#!/usr/bin/env python3
import http.server, socketserver, ssl, subprocess, os, sys

DOMAIN = "aipoc.creatingwow.in"
PORT = 443

def setup():
    # Generate certificate
    if not os.path.exists(f"{DOMAIN}.crt"):
        subprocess.run(["openssl", "req", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048", 
                       "-keyout", f"{DOMAIN}.key", "-out", f"{DOMAIN}.crt", "-subj", f"/CN={DOMAIN}"], check=True)
    
    # Add host entry
    try:
        with open('/etc/hosts', 'r') as f:
            if DOMAIN not in f.read():
                subprocess.run(["sudo", "sh", "-c", f"echo '127.0.0.1 {DOMAIN}' >> /etc/hosts"], check=True)
    except: pass

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup()
        print(f"✅ Setup complete for {DOMAIN}")
    else:
        if not os.path.exists(f"{DOMAIN}.crt"):
            print("Run: python3 https_server.py setup")
            sys.exit(1)
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(f"{DOMAIN}.crt", f"{DOMAIN}.key")
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            print(f"🚀 https://{DOMAIN}")
            httpd.serve_forever()