# HTTPS Server for aipoc.creatingwow.in

Single-file HTTPS server with automatic certificate generation and host configuration.

## Quick Start

```bash
# Setup (generates certificate + adds host entry)
python3 https_server.py setup

# Run server
sudo python3 https_server.py
```

## Access
- URL: https://aipoc.creatingwow.in
- Port: 443 (HTTPS)

## Files Created
- `aipoc.creatingwow.in.crt` - SSL certificate
- `aipoc.creatingwow.in.key` - SSL private key
- `/etc/hosts` entry: `127.0.0.1 aipoc.creatingwow.in`

## Requirements
- Python 3
- OpenSSL
- sudo access (for port 443 and /etc/hosts)