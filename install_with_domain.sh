#!/bin/bash

# SMBC Complete Installation with Domain Setup

set -e

DOMAIN=${1:-"localhost"}

echo "🚀 Complete SMBC Risk Management Suite Installation"
echo "📍 Domain: $DOMAIN"
echo ""

# Run main installation
echo "📦 Step 1: Installing application dependencies..."
./install.sh

# Setup domain configuration
echo "🌐 Step 2: Setting up domain configuration..."
./setup_domain.sh "$DOMAIN"

echo ""
echo "✅ Complete installation finished!"
echo ""
echo "🎯 Quick Start:"
echo "1. Update .env with your database and API credentials"
echo "2. Start the application: ./start_fullstack.sh"
echo "3. Access at: http://$DOMAIN"
echo ""
echo "🔧 Admin Access:"
echo "   Username: admin"
echo "   Password: admin123"