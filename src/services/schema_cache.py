import json
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from src.core.config import Config
from src.utils.console import Console

class SchemaCache:
    def __init__(self, cache_file="schema_cache.json"):
        self.cache_file = cache_file
        self.config = Config()
        self.engine = create_engine(self.config.mysql_connection_string)
    
    def fetch_schema(self, database: str = None) -> str:
        if database is None:
            database = self.config.MYSQL_DATABASE
            
        schema_description = ""
        with self.engine.connect() as conn:
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = :db
                ORDER BY table_name
            """
            tables = conn.execute(text(tables_query), {"db": database}).fetchall()

            for (table_name,) in tables:
                if self.config.ALLOWED_TABLES and table_name not in self.config.ALLOWED_TABLES:
                    continue
                    
                schema_description += f"\nTable: {table_name}\nColumns: "
                
                columns_query = """
                    SELECT column_name, data_type, is_nullable, column_default, column_key
                    FROM information_schema.columns 
                    WHERE table_schema = :db AND table_name = :table
                    ORDER BY ordinal_position
                """
                columns = conn.execute(
                    text(columns_query), 
                    {"db": database, "table": table_name}
                ).fetchall()

                col_defs = []
                for col_name, data_type, is_nullable, default, key in columns:
                    col_def = f"{col_name} ({data_type}"
                    if key == "PRI":
                        col_def += ", PRIMARY KEY"
                    if is_nullable == "NO":
                        col_def += ", NOT NULL"
                    if default:
                        col_def += f", DEFAULT {default}"
                    col_def += ")"
                    col_defs.append(col_def)
                
                schema_description += ", ".join(col_defs) + "\n"

        return schema_description.strip()
    
    def save_schema_to_cache(self, database: str = None):
        if database is None:
            database = self.config.MYSQL_DATABASE
            
        Console.processing(f"Generating schema for database: {database}")
        schema = self.fetch_schema(database)
        
        cache_data = {
            "database": database,
            "schema": schema,
            "generated_at": datetime.now().isoformat(),
            "table_count": schema.count("Table:")
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        Console.success(f"Schema cached to {self.cache_file}")
        Console.info(f"Database: {database}")
        Console.info(f"Tables found: {cache_data['table_count']}")
        Console.info(f"Generated at: {cache_data['generated_at']}")
        
        return schema
    
    def load_schema_from_cache(self) -> str:
        if not os.path.exists(self.cache_file):
            raise FileNotFoundError(f"Schema cache file {self.cache_file} not found. Run generate_schema() first.")
        
        with open(self.cache_file, 'r') as f:
            cache_data = json.load(f)
        
        Console.success("Schema loaded from cache")
        Console.info(f"Database: {cache_data['database']}")
        Console.info(f"Tables: {cache_data['table_count']}")
        Console.info(f"Generated: {cache_data['generated_at']}")
        
        return cache_data['schema']
    
    def get_cache_info(self):
        if not os.path.exists(self.cache_file):
            return None
        
        with open(self.cache_file, 'r') as f:
            cache_data = json.load(f)
        
        return {
            "database": cache_data['database'],
            "table_count": cache_data['table_count'],
            "generated_at": cache_data['generated_at'],
            "file_size": os.path.getsize(self.cache_file)
        }
    
    def is_cache_valid(self) -> bool:
        return os.path.exists(self.cache_file)