from openai import OpenAI
from src.core.config import Config

class AIService:
    def __init__(self):
        self.config = Config()
        self.config.validate()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
    
    def question_to_sql(self, question: str, schema: str) -> str:
        # Handle system/administrative queries first
        question_lower = question.lower()
        
        # MySQL system queries
        if ("show" in question_lower or "all" in question_lower) and "users" in question_lower:
            if "active" in question_lower:
                return "SHOW PROCESSLIST;"
            else:
                return "SELECT User, Host FROM mysql.user;"
        elif "active" in question_lower and "user" in question_lower:
            return "SHOW PROCESSLIST;"
        elif "show" in question_lower and "databases" in question_lower:
            return "SHOW DATABASES;"
        elif "show" in question_lower and "tables" in question_lower:
            return "SHOW TABLES;"
        elif "show" in question_lower and "processes" in question_lower:
            return "SHOW PROCESSLIST;"
        elif "current" in question_lower and "user" in question_lower:
            return "SELECT USER(), CURRENT_USER();"
        
        # Regular data queries
        prompt = f"""
You are an expert in SQL. Convert the following natural language question
into a syntactically correct MySQL query.

Database schema:
{schema}

Question: {question}

Rules:
- Only return the SQL query, no explanation, no markdown formatting
- Use proper MySQL syntax
- ALWAYS use JOINs when data spans multiple tables
- Look for relationships between tables (common column names, foreign keys)
- If asking for "all" records, limit to 10-20 rows for readability
- Include appropriate WHERE clauses for filtering
- Use table aliases for better readability
- Choose the most relevant tables and join them appropriately
- Consider using INNER JOIN, LEFT JOIN as needed based on the question

SQL Query:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500
            )

            sql_query = response.choices[0].message.content.strip()
            return self._clean_sql_output(sql_query)
            
        except Exception as e:
            raise Exception(f"AI service error: {e}")
    
    def _clean_sql_output(self, sql_query: str) -> str:
        if sql_query.startswith("```"):
            lines = sql_query.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            sql_query = "\n".join(lines)
        
        sql_query = sql_query.replace("sql\n", "").strip()
        
        if not sql_query.endswith(";"):
            sql_query += ";"
            
        return sql_query
    
    def explain_sql(self, sql_query: str) -> str:
        prompt = f"""
Explain this SQL query in simple terms:

{sql_query}

Provide a clear, concise explanation of what this query does and which table it's querying from."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Could not generate explanation: {e}"
    
    def generate_natural_response(self, question: str, sql_query: str, results: list) -> str:
        """Generate natural language response based on query results"""
        if not results:
            return f"I couldn't find any data for your question: '{question}'"
        
        # Prepare results summary
        row_count = len(results)
        if row_count == 1:
            result_summary = "1 result"
        else:
            result_summary = f"{row_count} results"
        
        # Sample data for context
        sample_data = ""
        if results and hasattr(results[0], '_fields'):
            columns = results[0]._fields[:3]  # First 3 columns
            sample_data = f"Columns include: {', '.join(columns)}"
        
        prompt = f"""
Generate a natural language response for this database query result.

Original question: {question}
SQL query executed: {sql_query}
Number of results: {row_count}
{sample_data}

Provide a conversational response that:
- Answers the original question in natural language
- Mentions the number of results found
- Summarizes key findings if applicable
- Keep it concise and helpful

Response:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Found {result_summary} for your question: '{question}'"
    
    def suggest_query_alternatives(self, question: str, failed_sql: str, schema: str) -> str:
        """Suggest alternative queries when original fails or returns no results"""
        prompt = f"""
The user asked: "{question}"
The generated SQL query was: {failed_sql}
But it returned no results or failed.

Database schema:
{schema}

Suggest 2-3 alternative approaches with actual SQL queries:
- Check for different date formats with example queries
- Suggest related tables or columns with sample SQL
- Recommend different filtering approaches with working queries
- Include queries to inspect available data

Format suggestions with SQL code blocks using ```sql``` for easy execution.
Provide practical, actionable suggestions."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return "Try checking the date format or available data in the tables."
    
    def fix_sql_query(self, failed_sql: str, error_message: str, schema: str) -> str:
        """Attempt to fix a failed SQL query based on error message"""
        prompt = f"""
This SQL query failed:
{failed_sql}

Error message:
{error_message}

Database schema:
{schema}

Fix the SQL query by:
- Correcting column names that don't exist
- Fixing syntax errors
- Using proper table names
- Adjusting data types or formats

Return only the corrected SQL query, no explanation:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=300
            )
            
            fixed_sql = response.choices[0].message.content.strip()
            return self._clean_sql_output(fixed_sql)
            
        except Exception as e:
            return None
    
    def generate_executive_report(self, question: str, sql_query: str, results: list, row_count: int) -> str:
        """Generate comprehensive executive summary report"""
        # Prepare data summary
        data_summary = ""
        if results and hasattr(results[0], '_fields'):
            columns = results[0]._fields
            data_summary = f"Data includes {len(columns)} columns: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}"
        
        # Sample data for analysis
        sample_rows = []
        for i, row in enumerate(results[:3]):
            if hasattr(row, '_fields'):
                row_dict = {col: row[j] for j, col in enumerate(row._fields)}
                sample_rows.append(str(row_dict)[:200])
            else:
                sample_rows.append(str(row)[:200])
        
        prompt = f"""
Generate a comprehensive executive summary report based on this database query analysis.

Original Business Question: {question}
SQL Query: {sql_query}
Total Records Found: {row_count}
{data_summary}

Sample Data:
{chr(10).join(sample_rows)}

Create a professional executive report with:

1. EXECUTIVE SUMMARY (2-3 sentences)
2. KEY FINDINGS (3-5 bullet points)
3. DATA INSIGHTS (analysis of patterns, trends, risks)
4. BUSINESS IMPLICATIONS (what this means for the organization)
5. RECOMMENDATIONS (2-3 actionable items)

Use professional business language, focus on insights rather than technical details.
Format with clear sections and bullet points for readability."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating executive report: {e}"