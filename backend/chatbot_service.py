import sys
import os

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import Config
from src.services.schema_cache import SchemaCache
from src.services.database import DatabaseManager
from src.services.ai_service import AIService

class ChatbotService:
    def __init__(self):
        self.config = Config()
        self.schema_cache = SchemaCache()
        self.db_manager = DatabaseManager()
        self.ai_service = AIService()
        self.schema = None
    
    def initialize(self):
        """Initialize the chatbot service"""
        # Test database connection
        if not self.db_manager.test_connection():
            raise Exception("Database connection failed")
        
        # Load or generate schema
        try:
            self.schema = self.schema_cache.load_schema_from_cache()
        except FileNotFoundError:
            self.schema = self.schema_cache.save_schema_to_cache()
    
    def test_connection(self):
        """Test database connection"""
        return self.db_manager.test_connection()
    
    def refresh_schema(self):
        """Refresh the database schema cache"""
        self.schema = self.schema_cache.save_schema_to_cache()
    
    def process_question(self, question: str):
        """Process a natural language question and return results"""
        try:
            # Generate SQL query
            sql_query = self.ai_service.question_to_sql(question, self.schema)
            formatted_sql = self.ai_service.format_sql(sql_query)
            
            # Execute query
            result = self.db_manager.execute_query(sql_query)
            
            if result["success"]:
                # Generate natural language response
                natural_response = self.ai_service.generate_natural_response(
                    question, sql_query, result["data"]
                )
                
                return {
                    "success": True,
                    "response": natural_response,
                    "sql_query": formatted_sql,
                    "data": result["data"],
                    "row_count": result["row_count"]
                }
            else:
                return {
                    "success": False,
                    "response": f"Query failed: {result['error']}",
                    "sql_query": formatted_sql,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Error processing question: {str(e)}",
                "error": str(e)
            }