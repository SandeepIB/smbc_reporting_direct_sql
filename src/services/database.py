from sqlalchemy import create_engine, text
from src.core.config import Config
from src.utils.console import Console

class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.config.validate()
        self.engine = create_engine(self.config.mysql_connection_string)
    
    def execute_query(self, sql: str):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                
                if self.config.ROW_LIMIT > 0:
                    rows = result.fetchmany(self.config.ROW_LIMIT)
                    if len(rows) == self.config.ROW_LIMIT:
                        Console.warning(f"Results limited to {self.config.ROW_LIMIT} rows")
                else:
                    rows = result.fetchall()
                
                return {"success": True, "data": rows, "row_count": len(rows)}
        except Exception as e:
            return {"success": False, "error": str(e), "data": None}
    
    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                return result.fetchone()[0] == 1
        except Exception as e:
            Console.error(f"Database connection failed: {e}")
            return False