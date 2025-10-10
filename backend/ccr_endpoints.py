# CCR Endpoints for main backend
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import List
import os
import shutil
import tempfile
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# CCR functionality
analysis_results = {}
temp_dir = None
crop_config = {"rows": 2, "cols": 3, "enabled": False}

# Import CCR modules
try:
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'smbc_reporting_tool', 'backend'))
    from analysis import analyze_all_graphs
    from report_generator import generate_ppt_report
    from image_cropper import process_uploaded_images
    CCR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"CCR modules not available: {e}")
    CCR_AVAILABLE = False

async def upload_images(files: List[UploadFile] = File(...)):
    """Upload chart images for CCR analysis"""
    if not CCR_AVAILABLE:
        raise HTTPException(status_code=503, detail="CCR functionality not available")
    
    global temp_dir
    
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    temp_dir = tempfile.mkdtemp()
    uploaded_files = []
    
    for file in files:
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
        
        file_path = os.path.join(temp_dir, file.filename)
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        uploaded_files.append(file_path)
    
    return {"message": f"Uploaded {len(uploaded_files)} files", "files": uploaded_files}

async def configure_cropping(config: dict):
    """Configure image cropping settings"""
    if not CCR_AVAILABLE:
        raise HTTPException(status_code=503, detail="CCR functionality not available")
    
    global crop_config
    crop_config.update(config)
    return {"message": "Cropping configuration updated", "config": crop_config}

async def analyze():
    """Analyze uploaded images with AI"""
    if not CCR_AVAILABLE:
        raise HTTPException(status_code=503, detail="CCR functionality not available")
    
    global analysis_results, temp_dir
    
    if not temp_dir or not os.path.exists(temp_dir):
        raise HTTPException(status_code=400, detail="No images uploaded")
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not set")
    
    try:
        files = [f for f in os.listdir(temp_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not files:
            raise HTTPException(status_code=400, detail="No valid image files found")
        
        logger.info(f"Crop config: {crop_config}")
        logger.info(f"Original files: {files}")
        
        # Clean up any existing block directories
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path) and ('block' in item.lower() or 'crop' in item.lower()):
                shutil.rmtree(item_path, ignore_errors=True)
        
        # Only crop images if explicitly enabled
        if crop_config["enabled"]:
            try:
                cropped_files = process_uploaded_images(temp_dir, crop_config["rows"], crop_config["cols"])
                logger.info(f"Cropped {len(cropped_files)} image blocks: {[os.path.basename(f) for f in cropped_files]}")
            except Exception as crop_error:
                logger.error(f"Cropping failed: {crop_error}")
                raise HTTPException(status_code=500, detail=f"Cropping failed: {str(crop_error)}")
        
        exec_summary, graph_insights = analyze_all_graphs(temp_dir, crop_config["enabled"])
        
        analysis_results = {
            "executive_summary": exec_summary,
            "graph_insights": [
                {
                    "title": insight["title"],
                    "trend": insight["trend"],
                    "recommendation": insight["recommendation"],
                    "filename": os.path.basename(insight["image_path"])
                }
                for insight in graph_insights
            ]
        }
        
        return analysis_results
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def download_report():
    """Download PowerPoint report with analysis"""
    if not CCR_AVAILABLE:
        raise HTTPException(status_code=503, detail="CCR functionality not available")
    
    global analysis_results, temp_dir
    
    if not analysis_results:
        raise HTTPException(status_code=400, detail="No analysis results available")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"SMBC_Report_{timestamp}.pptx"
        report_path = os.path.join(tempfile.gettempdir(), report_filename)
        
        graph_insights_full = []
        for insight in analysis_results["graph_insights"]:
            full_path = None
            for root, dirs, files in os.walk(temp_dir):
                if insight["filename"] in files:
                    full_path = os.path.join(root, insight["filename"])
                    break
            
            if not full_path:
                full_path = os.path.join(temp_dir, insight["filename"])
            
            if os.path.exists(full_path):
                graph_insights_full.append({
                    "image_path": full_path,
                    "title": insight["title"],
                    "trend": insight["trend"],
                    "recommendation": insight["recommendation"]
                })
        
        if graph_insights_full:
            generate_ppt_report(
                analysis_results["executive_summary"],
                graph_insights_full,
                report_path
            )
        else:
            raise Exception("No valid images found for report generation")
        
        return FileResponse(
            report_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=report_filename,
            headers={"Content-Disposition": f"attachment; filename={report_filename}"}
        )
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")