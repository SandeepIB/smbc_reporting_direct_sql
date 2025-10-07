#!/usr/bin/env python3
"""
Updated CLI application that uses the chatbot service
"""
import sys
from backend.chatbot_service import ChatbotService
from src.utils.console import Console

class CLIChatbot:
    def __init__(self):
        self.chatbot = ChatbotService()
        
    def initialize(self):
        """Initialize the CLI application"""
        Console.header("Prompts to Insights Application")
        Console.processing("Initializing application...")
        
        try:
            self.chatbot.initialize()
            Console.success("Application initialized successfully")
            return True
        except Exception as e:
            Console.error(f"Initialization failed: {e}")
            return False
    
    def process_question(self, question: str):
        """Process a question and display results"""
        Console.separator()
        Console.question(f"Question: {question}")
        
        Console.processing("Processing question...")
        result = self.chatbot.process_question(question)
        
        if result["success"]:
            Console.success("Query executed successfully")
            Console.info("SQL Query:")
            print(f"{Console.CYAN}{result['sql_query']}{Console.END}\n")
            
            Console.info("Answer:")
            print(f"{Console.GREEN}{result['response']}{Console.END}\n")
            
            if "data" in result and result["data"]:
                self._display_results(result["data"])
        else:
            Console.error(result["response"])
            if "sql_query" in result:
                Console.info("Generated SQL:")
                print(f"{Console.CYAN}{result['sql_query']}{Console.END}\n")
    
    def _display_results(self, rows):
        """Display query results"""
        if not rows:
            return
        
        display_limit = min(10, len(rows))
        
        print(f"\n{Console.BOLD}{Console.GREEN}📊 Results:{Console.END}")
        Console.separator()
        
        if rows and hasattr(rows[0], '_fields'):
            columns = rows[0]._fields
            Console.table_header(columns)
            for row in rows[:display_limit]:
                Console.table_row(row)
        else:
            for i, row in enumerate(rows[:display_limit], 1):
                print(f"{Console.CYAN}Row {i:2d}:{Console.END} {row}")
        
        if len(rows) > display_limit:
            Console.info(f"... and {len(rows) - display_limit} more rows")
    
    def interactive_mode(self):
        """Run in interactive mode"""
        Console.info("Interactive Mode - Ask questions about your data!")
        Console.info("Commands: 'quit' to exit, 'refresh' to reload schema")
        
        while True:
            try:
                question = input(f"\n{Console.BOLD}{Console.BLUE}> {Console.END}").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    Console.success("Goodbye!")
                    break
                elif question.lower() == 'refresh':
                    Console.processing("Refreshing schema...")
                    self.chatbot.refresh_schema()
                    Console.success("Schema refreshed")
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
    """Main CLI entry point"""
    cli = CLIChatbot()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "test-connection":
            Console.processing("Testing database connection...")
            if cli.chatbot.test_connection():
                Console.success("Connection successful!")
            else:
                Console.error("Connection failed!")
            return
        elif sys.argv[1] == "generate-schema":
            Console.processing("Generating schema cache...")
            cli.chatbot.refresh_schema()
            Console.success("Schema generated successfully")
            return
    
    # Initialize and run
    if not cli.initialize():
        sys.exit(1)
    
    # Check if question provided as argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        question = " ".join(sys.argv[1:])
        cli.process_question(question)
    else:
        cli.interactive_mode()

if __name__ == "__main__":
    main()