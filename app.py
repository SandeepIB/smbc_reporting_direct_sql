#!/usr/bin/env python3
"""
Natural Language to SQL Query Application

This application converts natural language questions into SQL queries
and executes them against a MySQL database.
"""

import sys
from src.core.config import Config
from src.services.schema_cache import SchemaCache
from src.services.database import DatabaseManager
from src.services.ai_service import AIService
from src.utils.console import Console

class NLToSQLApp:
    def __init__(self):
        self.config = Config()
        self.schema_cache = SchemaCache()
        self.db_manager = DatabaseManager()
        self.ai_service = AIService()
        self.last_question = None
        self.last_sql = None
        self.last_error = None
        self.suggested_queries = []
        self.last_results = None
        
    def initialize(self):
        """Initialize the application"""
        Console.header("Natural Language to SQL Application")
        Console.processing("Initializing application...")
        
        # Test database connection
        if not self.db_manager.test_connection():
            Console.error("Database connection failed!")
            return False
        
        Console.success("Database connection successful")
        
        # Load or generate schema
        try:
            schema = self.schema_cache.load_schema_from_cache()
        except FileNotFoundError:
            Console.info("No schema cache found, generating...")
            schema = self.schema_cache.save_schema_to_cache()
        
        self.schema = schema
        return True
    
    def process_question(self, question: str):
        """Process a natural language question"""
        Console.separator()
        Console.question(f"Question: {question}")
        
        # Store current context
        self.last_question = question
        
        try:
            # Generate SQL
            Console.processing("Converting to SQL...")
            sql_query = self.ai_service.question_to_sql(question, self.schema)
            self.last_sql = sql_query
            Console.success("Generated SQL:")
            print(f"\n{Console.CYAN}{sql_query}{Console.END}\n")
            
            # Execute SQL
            Console.processing("Executing query...")
            result = self.db_manager.execute_query(sql_query)
            
            if result["success"]:
                Console.success(f"Query executed successfully ({result['row_count']} rows)")
                
                if result['row_count'] > 0:
                    # Store results for report generation
                    self.last_results = {
                        'question': question,
                        'sql': sql_query,
                        'data': result['data'],
                        'row_count': result['row_count']
                    }
                    
                    # Generate natural language response
                    natural_response = self.ai_service.generate_natural_response(
                        question, sql_query, result["data"]
                    )
                    Console.info("Answer:")
                    print(f"{Console.GREEN}{natural_response}{Console.END}\n")
                    
                    self._display_results(result["data"])
                    Console.info("Type 'report' to generate an executive summary report")
                else:
                    Console.warning("No results found.")
                    self._suggest_alternatives(question, sql_query)
                
                # Optionally explain the query
                if input(f"\n{Console.PURPLE}Would you like an explanation of the SQL? (y/n): {Console.END}").lower() == 'y':
                    explanation = self.ai_service.explain_sql(sql_query)
                    Console.info("Explanation:")
                    print(f"{explanation}\n")
            else:
                self.last_error = result['error']
                Console.error(f"Query failed: {result['error']}")
                self._handle_query_error(question, sql_query, result['error'])
                
        except Exception as e:
            Console.error(f"Error processing question: {e}")
    
    def _display_results(self, rows):
        """Display query results in a formatted way"""
        if not rows:
            Console.warning("No results found.")
            return
        
        display_limit = min(10, len(rows))
        
        print(f"\n{Console.BOLD}{Console.GREEN}📊 Results:{Console.END}")
        Console.separator()
        
        # Display results with better formatting for wide tables
        if rows and hasattr(rows[0], '_fields'):
            columns = rows[0]._fields
            if len(columns) > 5:
                Console.warning(f"Table has {len(columns)} columns, showing first 5")
            Console.table_header(columns)
            for row in rows[:display_limit]:
                Console.table_row(row)
        else:
            for i, row in enumerate(rows[:display_limit], 1):
                if len(str(row)) > 200:
                    print(f"{Console.CYAN}Row {i:2d}:{Console.END} {str(row)[:200]}...")
                else:
                    print(f"{Console.CYAN}Row {i:2d}:{Console.END} {row}")
        
        if len(rows) > display_limit:
            Console.info(f"... and {len(rows) - display_limit} more rows")
    
    def _suggest_alternatives(self, question: str, sql_query: str):
        """Suggest alternatives when no results found"""
        suggestions = self.ai_service.suggest_query_alternatives(question, sql_query, self.schema)
        if suggestions:
            Console.info("Suggestions:")
            print(f"{Console.YELLOW}{suggestions}{Console.END}\n")
    
    def _handle_query_error(self, question: str, sql_query: str, error: str):
        """Handle query errors and suggest fixes"""
        Console.info("Let me try to fix this query...")
        
        try:
            fixed_query = self.ai_service.fix_sql_query(sql_query, error, self.schema)
            if fixed_query and fixed_query != sql_query:
                Console.info("Suggested fix:")
                print(f"{Console.CYAN}{fixed_query}{Console.END}\n")
                
                if input(f"{Console.PURPLE}Try this fixed query? (y/n): {Console.END}").lower() == 'y':
                    Console.processing("Executing fixed query...")
                    result = self.db_manager.execute_query(fixed_query)
                    
                    if result["success"]:
                        Console.success(f"Fixed query executed successfully ({result['row_count']} rows)")
                        
                        if result['row_count'] > 0:
                            natural_response = self.ai_service.generate_natural_response(
                                question, fixed_query, result["data"]
                            )
                            Console.info("Answer:")
                            print(f"{Console.GREEN}{natural_response}{Console.END}\n")
                            self._display_results(result["data"])
                        else:
                            Console.warning("Fixed query returned no results.")
                    else:
                        Console.error(f"Fixed query also failed: {result['error']}")
            else:
                suggestions = self.ai_service.suggest_query_alternatives(question, sql_query, self.schema)
                if suggestions:
                    Console.info("Suggestions:")
                    print(f"{Console.YELLOW}{suggestions}{Console.END}\n")
        except Exception as e:
            Console.error(f"Could not generate suggestions: {e}")
    
    def _generate_executive_report(self):
        """Generate executive summary report from last results"""
        if not self.last_results:
            Console.warning("No recent query results available for report generation.")
            return
        
        Console.processing("Generating executive summary report...")
        
        try:
            report = self.ai_service.generate_executive_report(
                self.last_results['question'],
                self.last_results['sql'],
                self.last_results['data'],
                self.last_results['row_count']
            )
            
            Console.header("Executive Summary Report")
            print(f"{Console.WHITE}{report}{Console.END}\n")
            
            # Ask if user wants to save report
            if input(f"{Console.PURPLE}Save report to file? (y/n): {Console.END}").lower() == 'y':
                self._save_report_to_file(report)
                
        except Exception as e:
            Console.error(f"Error generating report: {e}")
    
    def _save_report_to_file(self, report: str):
        """Save report to file"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"executive_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write("EXECUTIVE SUMMARY REPORT\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Query: {self.last_results['question']}\n")
                f.write(f"Records: {self.last_results['row_count']}\n\n")
                f.write(report)
                f.write("\n\n" + "=" * 60 + "\n")
                f.write(f"SQL Query:\n{self.last_results['sql']}\n")
            
            Console.success(f"Report saved to {filename}")
            
        except Exception as e:
            Console.error(f"Error saving report: {e}")
    
    def interactive_mode(self):
        """Run in interactive mode"""
        Console.info("Interactive Mode - Ask questions about your data!")
        Console.info("Commands: 'quit' to exit, 'refresh' to reload schema, 'retry' to try last question again")
        Console.info("          'report' to generate executive summary from last results")
        
        while True:
            try:
                question = input(f"\n{Console.BOLD}{Console.BLUE}> {Console.END}").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    Console.success("Goodbye!")
                    break
                elif question.lower() == 'refresh':
                    Console.processing("Refreshing schema...")
                    self.schema = self.schema_cache.save_schema_to_cache()
                    continue
                elif question.lower() in ['retry', 'try again'] and self.last_question:
                    Console.info("Retrying last question...")
                    self.process_question(self.last_question)
                    continue
                elif question.lower().startswith('fix') and self.last_error:
                    Console.info("Attempting to fix the last failed query...")
                    if self.last_sql and self.last_question:
                        self._handle_query_error(self.last_question, self.last_sql, self.last_error)
                    continue
                elif question.lower().startswith('report') and self.last_results:
                    self._generate_executive_report()
                    continue
                elif not question:
                    continue
                
                self.process_question(question)
                
            except KeyboardInterrupt:
                Console.success("\nGoodbye!")
                break
            except Exception as e:
                Console.error(f"Unexpected error: {e}")

def main():
    """Main application entry point"""
    app = NLToSQLApp()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "generate-schema":
            Console.processing("Generating schema cache...")
            app.schema_cache.save_schema_to_cache()
            return
        elif sys.argv[1] == "test-connection":
            Console.processing("Testing database connection...")
            if app.db_manager.test_connection():
                Console.success("Connection successful!")
            else:
                Console.error("Connection failed!")
            return
        elif sys.argv[1] == "schema-info":
            info = app.schema_cache.get_cache_info()
            if info:
                Console.header("Schema Cache Information")
                Console.info(f"Database: {info['database']}")
                Console.info(f"Tables: {info['table_count']}")
                Console.info(f"Generated: {info['generated_at']}")
                Console.info(f"File size: {info['file_size']} bytes")
            else:
                Console.error("No schema cache found")
            return
    
    # Initialize and run
    if not app.initialize():
        sys.exit(1)
    
    # Check if question provided as argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        question = " ".join(sys.argv[1:])
        app.process_question(question)
    else:
        app.interactive_mode()

if __name__ == "__main__":
    main()