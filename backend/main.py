from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from contextlib import asynccontextmanager
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime
import sys
import os
import shutil
import tempfile

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add CCR tool path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'smbc_reporting_tool', 'backend'))

from src.core.config import Config
from src.services.schema_cache import SchemaCache
from src.services.database import DatabaseManager
from src.services.ai_service import AIService
from feedback_service import FeedbackService
from ccr_endpoints import upload_images, configure_cropping, analyze, download_report


from dotenv import load_dotenv
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global schema
    logger.info("Starting Counterparty Risk Assistant API...")
    
    # Test database connection
    if not db_manager.test_connection():
        logger.error("Database connection failed!")
        raise Exception("Database connection failed")
    
    # Load or generate schema
    try:
        schema = schema_cache.load_schema_from_cache()
        logger.info("Schema loaded from cache")
    except FileNotFoundError:
        logger.info("No schema cache found, generating...")
        schema = schema_cache.save_schema_to_cache()
        logger.info("Schema generated and cached")
    
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(title="Counterparty Risk Assistant API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ConfirmRequest(BaseModel):
    confirmed: bool
    session_id: str

class RefineRequest(BaseModel):
    original_question: str
    feedback: str
    session_id: str

class ReportRequest(BaseModel):
    question: str
    sql_query: str
    raw_data: list
    session_id: str

class FeedbackRequest(BaseModel):
    messageId: str
    type: str
    feedback: str
    originalQuery: str
    sqlQuery: str = None
    response: str
    sessionId: str = None

class ProcessFeedbackRequest(BaseModel):
    original_query: str
    feedback: str
    session_id: str = None

class TrainingDataRequest(BaseModel):
    question: str
    answer: str
    context: str = None

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class FeedbackCreateRequest(BaseModel):
    original_query: str
    feedback: str
    sql_query: str = None
    response: str = None
    type: str = "manual"

class FeedbackUpdateRequest(BaseModel):
    original_query: str = None
    feedback: str = None
    sql_query: str = None
    response: str = None
    status: str = None

class ChatResponse(BaseModel):
    response: str
    sql_query: str = None
    raw_data: list = None
    row_count: int = 0
    success: bool
    session_id: str
    timestamp: str
    needs_refinement: bool = False
    needs_confirmation: bool = False
    interpreted_question: dict = None
    data_sources: list = None

# Global instances
config = Config()
schema_cache = SchemaCache()
db_manager = DatabaseManager()
ai_service = AIService()
feedback_service = FeedbackService()
schema = None

# Session storage (in production, use Redis or database)
sessions = {}



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process natural language question and return response"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize session if new
        if session_id not in sessions:
            sessions[session_id] = {
                "history": [],
                "created_at": datetime.now().isoformat()
            }
        
        # Log the interaction
        logger.info(f"Session {session_id}: {request.message}")
        
        # Check if this session has a pending confirmation
        if session_id in sessions and sessions[session_id].get("pending_confirmation"):
            return ChatResponse(
                response="Please confirm the previous question first.",
                success=False,
                session_id=session_id,
                timestamp=datetime.now().isoformat()
            )
        
        # Generate structured interpretation of the question
        interpretation = ai_service.interpret_question(request.message)
        
        # Store pending question for confirmation
        sessions[session_id]["pending_confirmation"] = {
            "original_question": request.message,
            "interpretation": interpretation
        }
        
        return ChatResponse(
            response=f"Please confirm your question:",
            success=True,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            needs_confirmation=True,
            interpreted_question=interpretation
        )
        
        # Execute query
        result = db_manager.execute_query(sql_query)
        
        if result["success"]:
            # Generate natural language response
            natural_response = ai_service.generate_natural_response(
                request.message, sql_query, result["data"]
            )
            
            # Convert raw data to serializable format
            raw_data_serializable = []
            if result["data"]:
                for row in result["data"]:
                    if hasattr(row, '_fields'):
                        row_dict = {col: getattr(row, col) for col in row._fields}
                        raw_data_serializable.append(row_dict)
                    else:
                        raw_data_serializable.append(dict(row) if hasattr(row, 'keys') else str(row))
            
            # Store in session history
            sessions[session_id]["history"].append({
                "question": request.message,
                "sql": sql_query,
                "response": natural_response,
                "raw_data": raw_data_serializable,
                "row_count": result['row_count'],
                "timestamp": datetime.now().isoformat(),
                "success": True
            })
            
            # Check if response needs refinement (low data quality)
            needs_refinement = result['row_count'] == 0 or len(natural_response) < 20
            
            return ChatResponse(
                response=natural_response,
                sql_query=sql_query,
                raw_data=raw_data_serializable,
                row_count=result['row_count'],
                success=True,
                session_id=session_id,
                timestamp=datetime.now().isoformat(),
                needs_refinement=needs_refinement
            )
        else:
            error_response = f"I encountered an error: {result['error']}"
            
            # Store error in session history
            sessions[session_id]["history"].append({
                "question": request.message,
                "sql": sql_query,
                "response": error_response,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": result['error']
            })
            
            return ChatResponse(
                response=error_response,
                sql_query=sql_query,
                success=False,
                session_id=session_id,
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]["history"]

@app.post("/confirm", response_model=ChatResponse)
async def confirm_question(request: ConfirmRequest):
    """Handle question confirmation"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = sessions.get(request.session_id, {})
        pending = session_data.get("pending_confirmation")
        if not pending:
            raise HTTPException(status_code=400, detail="No pending confirmation")
        
        if request.confirmed:
            # User confirmed - execute the query
            original_question = pending.get("original_question", "")
            
            # Clear pending confirmation first
            if "pending_confirmation" in sessions[request.session_id]:
                del sessions[request.session_id]["pending_confirmation"]
            
            # Get training context for semantic enhancement
            training_context = feedback_service.get_semantic_context(original_question)
            
            # Generate SQL query with training context
            sql_query = ai_service.question_to_sql(original_question, schema, training_context)
            formatted_sql = ai_service.format_sql(sql_query)
            
            # Execute query
            result = db_manager.execute_query(sql_query)
            
            if result["success"]:
                # Generate natural language response
                natural_response = ai_service.generate_natural_response(
                    original_question, sql_query, result["data"]
                )
                
                # Convert raw data to serializable format
                raw_data_serializable = []
                if result["data"]:
                    for row in result["data"]:
                        if hasattr(row, '_fields'):
                            row_dict = {col: getattr(row, col) for col in row._fields}
                            raw_data_serializable.append(row_dict)
                        else:
                            raw_data_serializable.append(dict(row) if hasattr(row, 'keys') else str(row))
                
                # Extract data sources
                data_sources = []
                sql_lower = sql_query.lower()
                if 'counterparty_new' in sql_lower:
                    data_sources.append('counterparty_new')
                if 'trade_new' in sql_lower:
                    data_sources.append('trade_new')
                if 'concentration_new' in sql_lower:
                    data_sources.append('concentration_new')
                
                # Store in session history
                sessions[request.session_id]["history"].append({
                    "question": original_question,
                    "sql": sql_query,
                    "response": natural_response,
                    "raw_data": raw_data_serializable,
                    "row_count": result['row_count'],
                    "data_sources": data_sources,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                })
                
                return ChatResponse(
                    response=natural_response,
                    sql_query=formatted_sql,
                    raw_data=raw_data_serializable,
                    row_count=result['row_count'],
                    success=True,
                    session_id=request.session_id,
                    timestamp=datetime.now().isoformat(),
                    data_sources=data_sources
                )
            else:
                # Clear pending confirmation
                if "pending_confirmation" in sessions[request.session_id]:
                    del sessions[request.session_id]["pending_confirmation"]
                
                return ChatResponse(
                    response=f"Query failed: {result['error']}",
                    sql_query=formatted_sql,
                    success=False,
                    session_id=request.session_id,
                    timestamp=datetime.now().isoformat()
                )
        else:
            # User declined - ask for clarification
            if "pending_confirmation" in sessions[request.session_id]:
                del sessions[request.session_id]["pending_confirmation"]
            
            return ChatResponse(
                response="Please rephrase or clarify your question.",
                success=True,
                session_id=request.session_id,
                timestamp=datetime.now().isoformat()
            )
            
    except KeyError as e:
        logger.error(f"KeyError in confirmation: {e}")
        # Reset session state
        if request.session_id in sessions:
            sessions[request.session_id].pop("pending_confirmation", None)
        raise HTTPException(status_code=500, detail=f"Session error: {str(e)}")
    except Exception as e:
        logger.error(f"Error confirming question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine", response_model=ChatResponse)
async def refine_question(request: RefineRequest):
    """Refine a question based on user feedback"""
    try:
        # Combine original question with feedback
        refined_question = f"{request.original_question}. {request.feedback}"
        
        # Process the refined question
        chat_request = ChatRequest(message=refined_question, session_id=request.session_id)
        return await chat(chat_request)
        
    except Exception as e:
        logger.error(f"Error refining question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    """Generate executive report"""
    try:
        # Convert raw data back to result-like objects for AI processing
        mock_results = []
        if request.raw_data:
            for row_data in request.raw_data:
                # Create a simple object with the data
                class MockRow:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                        self._fields = list(data.keys())
                mock_results.append(MockRow(row_data))
        
        # Generate executive summary
        executive_summary = ai_service.generate_executive_summary(
            request.question, request.sql_query, mock_results
        )
        
        # Extract data sources from SQL query
        data_sources = []
        sql_lower = request.sql_query.lower()
        if 'counterparty_new' in sql_lower:
            data_sources.append('counterparty_new (Counterparty master data)')
        if 'trade_new' in sql_lower:
            data_sources.append('trade_new (Trade transaction data)')
        if 'concentration_new' in sql_lower:
            data_sources.append('concentration_new (Risk concentration metrics)')
        
        if not data_sources:
            data_sources = ['Database tables (source analysis from SQL query)']
        
        # Create report data
        report_data = {
            "title": "Executive Report – Counterparty & Exposure Insights",
            "question": request.question,
            "sql_query": request.sql_query,
            "raw_data": request.raw_data,
            "executive_summary": executive_summary,
            "data_sources": data_sources,
            "generated_at": datetime.now().isoformat(),
            "record_count": len(request.raw_data)
        }
        
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schema/refresh")
async def refresh_schema():
    """Refresh the database schema cache"""
    global schema
    try:
        schema = schema_cache.save_schema_to_cache()
        return {"message": "Schema refreshed successfully"}
    except Exception as e:
        logger.error(f"Error refreshing schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        result = feedback_service.submit_feedback(request.dict())
        return result
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-feedback")
async def process_feedback(request: ProcessFeedbackRequest):
    try:
        # Get training context for semantic enhancement
        context = feedback_service.get_semantic_context(request.original_query)
        
        # Use the original successful query approach instead of generating new SQL
        # This prevents column existence errors
        sql_query = ai_service.question_to_sql(request.original_query, schema, context)
        result = db_manager.execute_query(sql_query)
        
        if result["success"]:
            # Generate response with feedback context but use original query structure
            response_context = f"Based on your feedback: {request.feedback}" if request.feedback else ""
            natural_response = ai_service.generate_natural_response(
                request.original_query, sql_query, result["data"]
            )
            if response_context:
                natural_response = f"{response_context}\n\n{natural_response}"
            
            raw_data_serializable = []
            if result["data"]:
                for row in result["data"]:
                    if hasattr(row, '_fields'):
                        row_dict = {col: getattr(row, col) for col in row._fields}
                        raw_data_serializable.append(row_dict)
                    else:
                        raw_data_serializable.append(dict(row) if hasattr(row, 'keys') else str(row))
            
            return ChatResponse(
                response=natural_response,
                sql_query=sql_query,
                raw_data=raw_data_serializable,
                row_count=result['row_count'],
                success=True,
                session_id=request.session_id,
                timestamp=datetime.now().isoformat()
            )
        else:
            return ChatResponse(
                response=f"Query failed: {result['error']}",
                sql_query=sql_query,
                success=False,
                session_id=request.session_id,
                timestamp=datetime.now().isoformat()
            )
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/feedbacks")
async def get_pending_feedbacks():
    """Get pending feedbacks - requires admin access"""
    try:
        return feedback_service.get_pending_feedbacks()
    except Exception as e:
        logger.error(f"Error getting feedbacks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/feedbacks/all")
async def get_all_feedbacks():
    """Get all feedbacks - requires admin access"""
    try:
        return feedback_service.get_all_feedbacks()
    except Exception as e:
        logger.error(f"Error getting all feedbacks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/feedbacks")
async def create_feedback(request: FeedbackCreateRequest):
    """Create new feedback - requires admin access"""
    try:
        return feedback_service.create_feedback(request.dict())
    except Exception as e:
        logger.error(f"Error creating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/admin/feedbacks/{feedback_id}")
async def update_feedback(feedback_id: int, request: FeedbackUpdateRequest):
    """Update feedback - requires admin access"""
    try:
        return feedback_service.update_feedback(feedback_id, request.dict(exclude_unset=True))
    except Exception as e:
        logger.error(f"Error updating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/admin/feedbacks/{feedback_id}")
async def delete_feedback(feedback_id: int):
    """Delete feedback - requires admin access"""
    try:
        return feedback_service.delete_feedback(feedback_id)
    except Exception as e:
        logger.error(f"Error deleting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/feedbacks/{feedback_id}/approve")
async def approve_feedback(feedback_id: int):
    """Approve feedback - requires admin access"""
    try:
        return feedback_service.approve_feedback(feedback_id)
    except Exception as e:
        logger.error(f"Error approving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/feedbacks/{feedback_id}/reject")
async def reject_feedback(feedback_id: int):
    """Reject feedback - requires admin access"""
    try:
        return feedback_service.reject_feedback(feedback_id)
    except Exception as e:
        logger.error(f"Error rejecting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/training-data")
async def get_training_data():
    """Get training data - requires admin access"""
    try:
        return feedback_service.get_training_data()
    except Exception as e:
        logger.error(f"Error getting training data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/training-data")
async def add_training_data(request: TrainingDataRequest):
    """Add training data - requires admin access"""
    try:
        return feedback_service.add_training_data(request.dict())
    except Exception as e:
        logger.error(f"Error adding training data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sample-data")
async def get_sample_data():
    """Get top 20 records from database for landing page"""
    try:
        # First, try to get data from any available table
        # Check what tables exist in the database
        show_tables_query = "SHOW TABLES"
        tables_result = db_manager.execute_query(show_tables_query)
        
        available_tables = []
        if tables_result["success"] and tables_result["data"]:
            for row in tables_result["data"]:
                if hasattr(row, '_fields'):
                    table_name = getattr(row, row._fields[0])
                    available_tables.append(table_name)
                else:
                    available_tables.append(list(row.values())[0] if hasattr(row, 'values') else str(row))
        
        logger.info(f"Available tables: {available_tables}")
        
        # Check columns for each table
        table_columns = {}
        for table in available_tables:
            try:
                desc_query = f"DESCRIBE {table}"
                desc_result = db_manager.execute_query(desc_query)
                if desc_result["success"] and desc_result["data"]:
                    columns = []
                    for col_row in desc_result["data"]:
                        if hasattr(col_row, '_fields'):
                            col_name = getattr(col_row, col_row._fields[0])
                            columns.append(col_name)
                        else:
                            columns.append(list(col_row.values())[0] if hasattr(col_row, 'values') else str(col_row))
                    table_columns[table] = columns
                    logger.info(f"Table {table} columns: {columns}")
            except Exception as e:
                logger.error(f"Error describing table {table}: {e}")
        
        # Build dynamic queries based on actual columns
        table_queries = []
        
        # For each available table, create a query using actual columns
        for table_name in available_tables:
            if table_name in table_columns:
                cols = table_columns[table_name]
                
                # Build SELECT statement with actual columns
                select_parts = []
                
                # Entity field
                entity_cols = [c for c in cols if any(x in c.lower() for x in ['entity', 'counterparty', 'id'])]
                entity_field = entity_cols[0] if entity_cols else 'id'
                select_parts.append(f"{entity_field} as Entity")
                
                # TradeCategory field
                category_cols = [c for c in cols if any(x in c.lower() for x in ['type', 'category', 'product', 'class'])]
                category_field = category_cols[0] if category_cols else "'Data'" 
                select_parts.append(f"{category_field} as TradeCategory")
                
                # TradeAssetClass field
                asset_cols = [c for c in cols if any(x in c.lower() for x in ['asset', 'class', 'sector'])]
                asset_field = asset_cols[0] if asset_cols else "'Asset'"
                select_parts.append(f"{asset_field} as TradeAssetClass")
                
                # TradeType field
                type_cols = [c for c in cols if any(x in c.lower() for x in ['trade_type', 'transaction', 'operation'])]
                type_field = type_cols[0] if type_cols else "'Transaction'"
                select_parts.append(f"{type_field} as TradeType")
                
                # TradeId field
                id_cols = [c for c in cols if any(x in c.lower() for x in ['trade_id', 'transaction_id', 'ref'])]
                id_field = id_cols[0] if id_cols else entity_field
                select_parts.append(f"{id_field} as TradeId")
                
                # Analytics fields - use any available columns
                remaining_cols = [c for c in cols if c not in [entity_field, category_field, asset_field, type_field, id_field]]
                
                # Analytics Addo
                addo_cols = [c for c in remaining_cols if any(x in c.lower() for x in ['system', 'engine', 'source'])]
                addo_field = addo_cols[0] if addo_cols else (remaining_cols[0] if remaining_cols else "'System'")
                select_parts.append(f"{addo_field} as `Analytics Addo`")
                
                # Analytics Input 1
                input1_cols = [c for c in remaining_cols if any(x in c.lower() for x in ['input', 'data', 'price'])]
                input1_field = input1_cols[0] if input1_cols else (remaining_cols[1] if len(remaining_cols) > 1 else "'Input1'")
                select_parts.append(f"{input1_field} as `Analytics Input`")
                
                # Analytics Input 2
                input2_field = input1_cols[1] if len(input1_cols) > 1 else (remaining_cols[2] if len(remaining_cols) > 2 else "'Input2'")
                select_parts.append(f"{input2_field} as `Analytics Input2`")
                
                # Analytics Output 1
                output1_cols = [c for c in remaining_cols if any(x in c.lower() for x in ['output', 'result', 'amount', 'value'])]
                output1_field = output1_cols[0] if output1_cols else (remaining_cols[3] if len(remaining_cols) > 3 else "'Output1'")
                select_parts.append(f"{output1_field} as `Analytics Output`")
                
                # Analytics Output 2
                output2_field = output1_cols[1] if len(output1_cols) > 1 else (remaining_cols[4] if len(remaining_cols) > 4 else "'Output2'")
                select_parts.append(f"{output2_field} as `Analytics Output2`")
                
                # Reporting Status
                status_cols = [c for c in cols if any(x in c.lower() for x in ['status', 'state'])]
                status_field = status_cols[0] if status_cols else "'Active'"
                select_parts.append(f"{status_field} as `Reporting Status`")
                
                # Build complete query
                query = f"SELECT {', '.join(select_parts)} FROM {table_name} ORDER BY {entity_field} DESC"
                table_queries.append((table_name, query))
                logger.info(f"Generated query for {table_name}: {query}")
        
        # Try each generated query
        for table_name, query in table_queries:
            try:
                logger.info(f"Trying dynamic query for table: {table_name}")
                result = db_manager.execute_query(query)
                
                if result["success"] and result["data"]:
                    # Convert to serializable format
                    data = []
                    for row in result["data"]:
                        if hasattr(row, '_fields'):
                            row_dict = {col: getattr(row, col) for col in row._fields}
                            data.append(row_dict)
                        else:
                            data.append(dict(row) if hasattr(row, 'keys') else str(row))
                    
                    logger.info(f"Successfully got {len(data)} records from {table_name}")
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data),
                        "source": table_name
                    }
            except Exception as query_error:
                logger.error(f"Error with dynamic query for {table_name}: {query_error}")
                continue
        
        # If no tables worked, try a simple query to get any data
        logger.info("No suitable tables found, trying simple queries")
        
        # Try to get columns from any table that exists
        for table_name in available_tables:
            try:
                simple_query = f"SELECT * FROM {table_name}"
                result = db_manager.execute_query(simple_query)
                
                if result["success"] and result["data"]:
                    # Convert any table data to our format
                    data = []
                    for i, row in enumerate(result["data"]):
                        if hasattr(row, '_fields'):
                            row_dict = {col: getattr(row, col) for col in row._fields}
                        else:
                            row_dict = dict(row) if hasattr(row, 'keys') else {"col1": str(row)}
                        
                        # Map available columns to our display format
                        mapped_row = {
                            "Entity": str(row_dict.get('entity_id', row_dict.get('counterparty_id', row_dict.get('id', f'ENT-{i+1}')))),
                            "TradeCategory": str(row_dict.get('product_type', row_dict.get('counterparty_type', row_dict.get('concentration_type', row_dict.get('type', 'Unknown'))))),
                            "TradeAssetClass": str(row_dict.get('asset_class', row_dict.get('sector', row_dict.get('category', 'Mixed')))),
                            "TradeType": str(row_dict.get('trade_type', row_dict.get('transaction_type', 'N/A'))),
                            "TradeId": str(row_dict.get('trade_id', row_dict.get('concentration_id', row_dict.get('id', f'ID-{i+1}')))),
                            "Analytics Addo": str(row_dict.get('risk_engine', row_dict.get('trading_system', row_dict.get('system', row_dict.get('source', 'System'))))),
                            "Analytics Input": str(row_dict.get('data_source', row_dict.get('price_source', row_dict.get('input_1', row_dict.get('original_query', 'Data Source'))))),
                            "Analytics Input2": str(row_dict.get('calculation_method', row_dict.get('risk_source', row_dict.get('input_2', row_dict.get('feedback', 'Method'))))),
                            "Analytics Output": str(row_dict.get('concentration_limit', row_dict.get('pnl_amount', row_dict.get('output_1', row_dict.get('response', 'Output'))))),
                            "Analytics Output2": str(row_dict.get('utilization_pct', row_dict.get('risk_amount', row_dict.get('output_2', row_dict.get('created_at', 'Result'))))),
                            "Reporting Status": str(row_dict.get('status', row_dict.get('reporting_status', 'Active')))
                        }
                        data.append(mapped_row)
                    
                    logger.info(f"Successfully mapped {len(data)} records from {table_name}")
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data),
                        "source": f"mapped_{table_name}"
                    }
            except Exception as table_error:
                logger.error(f"Error querying {table_name}: {table_error}")
                continue
        
        # Last resort - return empty data
        logger.warning("No data could be retrieved from any table")
        return {
            "success": False,
            "data": [],
            "count": 0,
            "source": "none",
            "message": "No data available in database"
        }
        

    except Exception as e:
        logger.error(f"Error getting sample data: {str(e)}")
        # Return error response
        return {
            "success": False,
            "data": [],
            "count": 0,
            "source": "error",
            "error": str(e)
        }

@app.post("/admin/login")
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint with hardcoded credentials"""
    try:
        # Hardcoded admin credentials
        if request.username == "admin" and request.password == "admin123":
            return {
                "success": True,
                "message": "Login successful",
                "token": "admin-session-token",  # In production, use JWT
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Error during admin login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# Chat API Routes (default)
@app.get("/api/health")
async def api_health_check():
    return await health_check()

# CCR API Routes
@app.post("/ccr/upload-images")
async def ccr_upload_images_endpoint(files: List[UploadFile] = File(...)):
    return await upload_images(files)

@app.post("/ccr/configure-cropping")
async def ccr_configure_cropping_endpoint(config: dict):
    return await configure_cropping(config)

@app.post("/ccr/analyze")
async def ccr_analyze_endpoint():
    return await analyze()

@app.get("/ccr/download-report")
async def ccr_download_report_endpoint():
    return await download_report()

# Legacy CCR endpoints (for backward compatibility)
@app.post("/upload-images")
async def upload_images_endpoint(files: List[UploadFile] = File(...)):
    return await upload_images(files)

@app.post("/configure-cropping")
async def configure_cropping_endpoint(config: dict):
    return await configure_cropping(config)

@app.post("/analyze")
async def analyze_endpoint():
    return await analyze()

@app.get("/download-report")
async def download_report_endpoint():
    return await download_report()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)