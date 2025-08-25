import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "phpmyadmin")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "StrongPasswordHere!")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "org_insights")
    
    ROW_LIMIT = int(os.environ.get("ROW_LIMIT", 500))
    ALLOWED_SCHEMAS = os.environ.get("ALLOWED_SCHEMAS", "").split(",") if os.environ.get("ALLOWED_SCHEMAS") else []
    ALLOWED_TABLES = os.environ.get("ALLOWED_TABLES", "").split(",") if os.environ.get("ALLOWED_TABLES") else []
    
    @property
    def mysql_connection_string(self):
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    def validate(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not all([self.MYSQL_HOST, self.MYSQL_USER, self.MYSQL_PASSWORD, self.MYSQL_DATABASE]):
            raise ValueError("MySQL connection parameters are required")