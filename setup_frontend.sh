#!/bin/bash

echo "🔧 Setting up frontend with security fixes..."

cd frontend

# Clean install to fix vulnerabilities
echo "📦 Cleaning node_modules and package-lock.json..."
rm -rf node_modules package-lock.json

# Update package.json with latest secure versions
echo "📝 Updating package.json with secure dependencies..."
cat > package.json << 'EOF'
{
  "name": "nl-to-sql-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "autoprefixer": "^10.4.16",
    "axios": "^1.6.2",
    "jspdf": "^2.5.1",
    "postcss": "^8.4.32",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "^5.0.1",
    "tailwindcss": "^3.3.6"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "overrides": {
    "nth-check": "^2.0.1",
    "postcss": "^8.4.32"
  }
}
EOF

# Install with legacy peer deps to avoid conflicts
echo "⬇️ Installing dependencies..."
npm install --legacy-peer-deps

# Fix vulnerabilities
echo "🔒 Fixing security vulnerabilities..."
npm audit fix --force

# Ensure react-scripts is installed
echo "📦 Ensuring react-scripts is available..."
npm install react-scripts@5.0.1 --save

echo "✅ Frontend setup complete!"
echo "🚀 You can now run: npm start"