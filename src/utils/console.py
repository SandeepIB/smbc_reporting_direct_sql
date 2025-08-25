"""Console formatting utilities"""

class Console:
    # Colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @staticmethod
    def success(message):
        print(f"{Console.GREEN}✅ {message}{Console.END}")
    
    @staticmethod
    def error(message):
        print(f"{Console.RED}❌ {message}{Console.END}")
    
    @staticmethod
    def warning(message):
        print(f"{Console.YELLOW}⚠️  {message}{Console.END}")
    
    @staticmethod
    def info(message):
        print(f"{Console.BLUE}ℹ️  {message}{Console.END}")
    
    @staticmethod
    def processing(message):
        print(f"{Console.CYAN}🔄 {message}{Console.END}")
    
    @staticmethod
    def question(message):
        print(f"{Console.PURPLE}❓ {message}{Console.END}")
    
    @staticmethod
    def header(title):
        print(f"\n{Console.BOLD}{Console.CYAN}{'='*60}{Console.END}")
        print(f"{Console.BOLD}{Console.CYAN}{title.center(60)}{Console.END}")
        print(f"{Console.BOLD}{Console.CYAN}{'='*60}{Console.END}\n")
    
    @staticmethod
    def separator():
        print(f"{Console.CYAN}{'-'*60}{Console.END}")
    
    @staticmethod
    def table_header(columns):
        if len(columns) > 5:
            columns = list(columns[:5]) + ["..."]
        header = " | ".join(f"{col:<20}" for col in columns)
        print(f"{Console.BOLD}{header}{Console.END}")
        print(f"{Console.CYAN}{'-'*len(header)}{Console.END}")
    
    @staticmethod
    def table_row(values):
        if len(values) > 5:
            values = list(values[:5]) + ["..."]
        row = " | ".join(f"{str(val)[:18]:<20}" for val in values)
        print(row)