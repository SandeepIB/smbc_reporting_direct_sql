from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import Config
from src.services.schema_cache import SchemaCache
from src.services.database import DatabaseManager
from src.services.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global schema
    logger.info("Starting Natural Language to SQL API...")
    
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

app = FastAPI(title="Natural Language to SQL API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
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

# Global instances
config = Config()
schema_cache = SchemaCache()
db_manager = DatabaseManager()
ai_service = AIService()
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
        
        pending = sessions[request.session_id].get("pending_confirmation")
        if not pending:
            raise HTTPException(status_code=400, detail="No pending confirmation")
        
        if request.confirmed:
            # User confirmed - execute the query
            original_question = pending["original_question"]
            
            # Generate SQL query
            sql_query = ai_service.question_to_sql(original_question, schema)
            
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
                
                # Store in session history
                sessions[request.session_id]["history"].append({
                    "question": original_question,
                    "sql": sql_query,
                    "response": natural_response,
                    "raw_data": raw_data_serializable,
                    "row_count": result['row_count'],
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                })
                
                # Clear pending confirmation
                del sessions[request.session_id]["pending_confirmation"]
                
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
                # Clear pending confirmation
                del sessions[request.session_id]["pending_confirmation"]
                
                return ChatResponse(
                    response=f"Query failed: {result['error']}",
                    sql_query=sql_query,
                    success=False,
                    session_id=request.session_id,
                    timestamp=datetime.now().isoformat()
                )
        else:
            # User declined - ask for clarification
            del sessions[request.session_id]["pending_confirmation"]
            
            return ChatResponse(
                response="Please rephrase or clarify your question.",
                success=True,
                session_id=request.session_id,
                timestamp=datetime.now().isoformat()
            )
            
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)