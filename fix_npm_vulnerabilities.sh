#!/bin/bash

echo "🔒 Quick fix for npm vulnerabilities..."

cd frontend

# Fix vulnerabilities automatically
npm audit fix

# If that doesn't work, force fix
if [ $? -ne 0 ]; then
    echo "⚠️ Standard fix failed, applying force fix..."
    npm audit fix --force
fi

# Update specific vulnerable packages
echo "📦 Updating specific vulnerable packages..."
npm update nth-check postcss

echo "✅ Vulnerability fixes applied!"
echo "ℹ️ Run 'npm audit' to check remaining issues"