# CCR Deck Assistant Integration

## Overview
The CCR Deck Assistant tool has been integrated into the main Prompts to Insights portal, allowing users to upload images, analyze them with AI, and generate PowerPoint reports.

## How to Use

### Starting the Application
```bash
# Start both main app and CCR tool
./start_with_ccr.sh
```

This will start:
- Main Backend API on port 8000
- CCR Backend API on port 8001  
- Frontend on port 3000

### Accessing CCR Deck Assistant
1. Open http://localhost:3000
2. Click on **"CCR Deck Assistant"** in the top navigation
3. Upload images using the file selector
4. Configure cropping settings if needed
5. Click "Analyze Images" to process with AI
6. Download the generated PowerPoint report

## Features

### Image Analysis
- Upload multiple images (PNG, JPG, JPEG)
- AI-powered analysis of charts and graphs
- Automatic cropping configuration
- Executive summary generation

### Report Generation
- PowerPoint report creation
- Individual graph insights
- Trend observations
- Business recommendations

## Architecture

### Frontend Integration
- `CCRDeckAssistant.js` - Main component
- `CCRDeckAssistant.css` - Styling
- Integrated into `LandingPage.js`

### Backend Services
- Main API: `http://localhost:8000` (Prompts to Insights)
- CCR API: `http://localhost:8001` (Image analysis & reporting)

### API Endpoints (CCR Tool)
- `POST /upload` - Upload images
- `POST /configure-cropping` - Set cropping parameters
- `GET /analyze` - Analyze uploaded images
- `GET /download-report` - Download PowerPoint report

## File Structure
```
smbc_reporting_direct_sql/
├── frontend/src/components/
│   ├── CCRDeckAssistant.js     # CCR component
│   └── CCRDeckAssistant.css    # CCR styles
├── smbc_reporting_tool/        # CCR backend
│   ├── backend/
│   ├── frontend/
│   └── utils/
└── start_with_ccr.sh          # Combined startup script
```

## Usage Workflow
1. **Navigation**: Click "CCR Deck Assistant" in header
2. **Upload**: Select image files containing charts/graphs
3. **Configure**: Enable/disable image cropping
4. **Analyze**: AI processes images and extracts insights
5. **Review**: View executive summary and graph insights
6. **Download**: Get PowerPoint report with findings

## Integration Benefits
- Single portal for all SMBC tools
- Consistent UI/UX across applications
- Shared authentication and session management
- Unified navigation and branding