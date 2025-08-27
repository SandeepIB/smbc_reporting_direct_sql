from openai import OpenAI
from src.core.config import Config

class AIService:
    def __init__(self):
        self.config = Config()
        self.config.validate()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
    
    def question_to_sql(self, question: str, schema: str) -> str:
        # Handle system queries only
        question_lower = question.lower()
        
        # MySQL system queries
        if (("show" in question_lower or "all" in question_lower) and "users" in question_lower):
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
Generate MySQL query using the exact schema provided.

Schema: {schema}
Question: {question}

CRITICAL TABLE AND COLUMN MAPPING:

TRADE_NEW table has: trade_id, notional_usd, batch_mtm, as_of_date, reporting_counterparty_id
COUNTERPARTY_NEW table has: counterparty_id, counterparty_sector, counterparty_name, mpe, mpe_limit
CONCENTRATION_NEW table has: counterparty_count, concentration_group, entity

IMPORTANT:
- MPE (Market Price Exposure) is in counterparty_new table
- counterparty_sector is ONLY in counterparty_new table
- counterparty_count is ONLY in concentration_new table
- For CCR portfolio exposure questions, use mpe from counterparty_new
- Always filter out NULL, empty, and zero values: mpe IS NOT NULL AND mpe != '' AND mpe != '0'
- Use correct aliases: t=trade_new, c=counterparty_new, con=concentration_new

CORRECT sector analysis example:
```sql
SELECT 
  c.counterparty_sector,
  COUNT(t.trade_id) as trade_count
FROM trade_new t
JOIN counterparty_new c ON t.reporting_counterparty_id = c.counterparty_id
GROUP BY c.counterparty_sector;
```

CORRECT concentration analysis example:
```sql
SELECT 
  con.concentration_group,
  SUM(CAST(con.counterparty_count AS UNSIGNED)) as total_count
FROM concentration_new con
GROUP BY con.concentration_group;
```

For time series analysis example:
```sql
SELECT 
  DATE_FORMAT(as_of_date, '%Y-%m') AS month,
  SUM(CAST(notional_usd AS DECIMAL(15,2))) as monthly_notional
FROM trade_new
WHERE YEAR(as_of_date) = 2024
GROUP BY month
ORDER BY month;
```

For MPE/CCR exposure analysis:
```sql
SELECT 
  DATE_FORMAT(as_of_date, '%Y-%m') AS month,
  SUM(CAST(mpe AS DECIMAL(15,2))) AS total_mpe,
  counterparty_sector
FROM counterparty_new
WHERE as_of_date LIKE '2024%' 
  AND mpe IS NOT NULL 
  AND mpe != '' 
  AND mpe != '0'
GROUP BY month, counterparty_sector
ORDER BY month;
```

For simple data exploration:
```sql
SELECT 
  c.counterparty_sector,
  SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional
FROM trade_new t
JOIN counterparty_new c ON t.reporting_counterparty_id = c.counterparty_id
WHERE t.notional_usd IS NOT NULL
GROUP BY c.counterparty_sector
ORDER BY total_notional DESC
LIMIT 10;
```

CRITICAL RESTRICTIONS:
- NEVER use LAG, LEAD, or any window functions
- NEVER use OVER clause
- NEVER use counterparty_count from counterparty_new (it doesn't exist there)
- counterparty_count is ONLY in concentration_new table
- Use ONLY basic SELECT, COUNT, SUM, AVG, MAX, MIN
- For time comparisons, use separate queries or subqueries
- Always use simple GROUP BY aggregations
- AVOID complex 3-table JOINs - use 2 tables maximum
- Always add WHERE clauses to filter NULL values
- Use LIMIT to ensure results are returned

Key rules:
- Check column exists in correct table before using
- For sectors: use counterparty_new.counterparty_sector
- For concentration: use concentration_new.counterparty_count
- For trades: use trade_new columns (notional_usd, trade_id, etc.)
- Keep queries simple and avoid complex analytical functions

FORBIDDEN FUNCTIONS: LAG, LEAD, OVER, WINDOW functions
USE ONLY: SELECT, FROM, WHERE, JOIN, GROUP BY, ORDER BY, COUNT, SUM, AVG

Return ONLY the SQL query:

SQL:"""

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
    
    def format_sql(self, sql_query: str) -> str:
        """Format SQL query for better readability"""
        if not sql_query:
            return sql_query
        
        # Basic SQL formatting
        formatted = sql_query.upper()
        
        # Add line breaks after major keywords
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 
                   'GROUP BY', 'ORDER BY', 'HAVING', 'UNION', 'AND', 'OR']
        
        for keyword in keywords:
            formatted = formatted.replace(f' {keyword} ', f'\n{keyword} ')
        
        # Clean up and add proper indentation
        lines = [line.strip() for line in formatted.split('\n') if line.strip()]
        formatted_lines = []
        
        for line in lines:
            if line.startswith(('SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'UNION')):
                formatted_lines.append(line)
            elif line.startswith(('JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN')):
                formatted_lines.append(f'  {line}')
            elif line.startswith(('AND', 'OR')):
                formatted_lines.append(f'  {line}')
            else:
                formatted_lines.append(f'  {line}')
        
        return '\n'.join(formatted_lines)
    
    def interpret_question(self, question: str) -> dict:
        """Provide structured interpretation of user question"""
        prompt = f"""
Analyze this user question and provide a structured interpretation in JSON format.

User question: {question}

Provide analysis in this exact JSON structure:
{{
  "data_requested": "What specific data/metrics they want (e.g., total trade notional, counterparty exposure)",
  "analysis_type": "What type of analysis (e.g., comparison between periods, ranking, trend analysis)",
  "context_significance": "Why this analysis matters in risk/finance context"
}}

Examples:
- "How did total trade notional change between 2023 and 2024?"
{{
  "data_requested": "Total trade notional (value of all executed trades)",
  "analysis_type": "Comparison between 2023 and 2024, with absolute and percentage changes",
  "context_significance": "Provides insight into shifts in exposure concentration and market activity"
}}

- "top 5 counterparties with highest exposure"
{{
  "data_requested": "Counterparty exposure rankings",
  "analysis_type": "Ranking analysis to identify top 5 counterparties by exposure amount",
  "context_significance": "Critical for concentration risk assessment and regulatory compliance"
}}

Return only valid JSON:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            import json
            content = response.choices[0].message.content.strip()
            # Clean up any markdown formatting
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(content)
            
        except Exception as e:
            # Fallback structure for any parsing errors
            return {
                "data_requested": f"Analysis of: {question}",
                "analysis_type": "Data query and analysis", 
                "context_significance": "Provides business insights from database"
            }
    
    def generate_natural_response(self, question: str, sql_query: str, results: list) -> str:
        """Generate risk analyst-style response using actual data"""
        if not results:
            return "No data found for this query."
        
        # Prepare actual data for AI analysis
        data_sample = ""
        if results:
            if hasattr(results[0], '_fields'):
                sample_rows = []
                for row in results:
                    row_dict = {col: getattr(row, col) for col in row._fields}
                    sample_rows.append(str(row_dict))
                data_sample = "\n".join(sample_rows)
            else:
                data_sample = "\n".join([str(row) for row in results])
        
        prompt = f"""
You are a senior risk analyst providing a briefing to a portfolio manager. Generate a concise, professional response using ONLY the actual data provided.

Question: {question}
Actual Data: {data_sample}

Rules:
- Use ONLY the exact names/values from the data (like TSE_C1, NASDAQ_C3, etc.)
- Write as a risk analyst explaining findings
- Use financial terms: exposure concentration, counterparty risk, long-dated trades
- Be concise (1-2 sentences max)
- NO placeholders or generic names
- Focus on risk implications

Examples:
- "TSE_C1 and NYSE_C4 represent the highest counterparty risk concentration in 2024."
- "Exposure concentration increased across five key counterparties: TSE_C1, TSE_C2, NASDAQ_C3, NYSE_C4, and CBOE_C5."
- "Long-dated exposure beyond 2026 is concentrated in NASDAQ_C3 and TSE_C2 positions."

Analyst Response:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to direct data extraction if AI fails
            values = []
            if hasattr(results[0], '_fields'):
                for row in results:
                    for col in row._fields:
                        val = getattr(row, col)
                        if val and str(val).strip() and str(val) != 'None':
                            values.append(str(val))
            
            if 'counterpart' in question.lower():
                return f"Counterparty risk concentration identified across {', '.join(values[:5])}."
            else:
                return f"Risk exposure analysis shows: {', '.join(values[:5])}."
    
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
    
    def generate_executive_summary(self, question: str, sql_query: str, results: list) -> str:
        """Generate executive summary for report"""
        # Prepare data for analysis
        data_sample = ""
        if results:
            if hasattr(results[0], '_fields'):
                sample_rows = []
                for row in results[:5]:
                    row_dict = {col: getattr(row, col) for col in row._fields}
                    sample_rows.append(str(row_dict))
                data_sample = "\n".join(sample_rows)
            else:
                data_sample = "\n".join([str(row) for row in results[:5]])
        
        prompt = f"""
Generate a concise executive summary for this database query result.

Question: {question}
Data Results: {data_sample}
Total Records: {len(results)}

Write a professional executive summary that:
- Highlights key findings and trends
- Mentions specific numbers/values from the data
- Identifies risks or business implications
- Uses financial/risk terminology
- Keep it 2-3 sentences maximum

Executive Summary:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Analysis of {len(results)} records shows key business insights related to the query."
    
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