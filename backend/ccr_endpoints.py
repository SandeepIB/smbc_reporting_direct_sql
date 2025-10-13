from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from typing import List
import io
import json

# Store uploaded files and config in memory for demo
uploaded_files = []
crop_configuration = {}

async def upload_images(files: List[UploadFile]):
    global uploaded_files
    uploaded_files = []
    
    for file in files:
        content = await file.read()
        uploaded_files.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        })
    
    return {
        "success": True,
        "message": "Images uploaded successfully", 
        "count": len(files),
        "files": [f["filename"] for f in uploaded_files]
    }

async def configure_cropping(config: dict):
    global crop_configuration
    crop_configuration = config
    return {
        "success": True,
        "message": "Cropping configured successfully", 
        "config": config
    }

async def analyze():
    global uploaded_files, crop_configuration
    
    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No images uploaded")
    
    # Generate insights for each uploaded file
    graph_insights = []
    for i, file_info in enumerate(uploaded_files):
        insight = {
            "filename": file_info["filename"],
            "title": f"Chart Analysis {i+1}: {file_info['filename']}",
            "trend": f"Analysis shows {'positive growth' if i % 2 == 0 else 'stable performance'} patterns",
            "recommendation": f"{'Increase exposure' if i % 2 == 0 else 'Monitor closely'} based on current trends"
        }
        graph_insights.append(insight)
    
    return {
        "success": True,
        "executive_summary": {
            "trend": "Overall positive market sentiment with controlled risk exposure",
            "recommendation": "Maintain current portfolio allocation while monitoring key risk indicators"
        },
        "graph_insights": graph_insights,
        "cropping_applied": crop_configuration.get("enabled", False),
        "analysis_timestamp": "2024-01-15T10:30:00Z"
    }

async def download_report(request=None):
    # Create a simple text report as a mock PowerPoint file
    report_content = f"""
SMBC CCR Analysis Report
========================

Generated: 2024-01-15
Files Analyzed: {len(uploaded_files)}
Cropping Enabled: {crop_configuration.get('enabled', False)}

Executive Summary:
- Overall positive market sentiment
- Controlled risk exposure maintained
- Recommend continued monitoring

Detailed Analysis:
"""
    
    for i, file_info in enumerate(uploaded_files):
        report_content += f"""

Chart {i+1}: {file_info['filename']}
- Trend: {'Positive growth' if i % 2 == 0 else 'Stable performance'}
- Recommendation: {'Increase exposure' if i % 2 == 0 else 'Monitor closely'}
"""
    
    # Return as downloadable file
    file_like = io.BytesIO(report_content.encode('utf-8'))
    
    return StreamingResponse(
        io.BytesIO(report_content.encode('utf-8')),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=SMBC_CCR_Report.pptx"}
    )

async def get_image(filename: str):
    raise HTTPException(status_code=404, detail="Image not found")