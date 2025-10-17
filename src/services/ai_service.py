from openai import OpenAI
from src.core.config import Config
import json
import pymysql
from datetime import datetime
import os


class AIService:
    def __init__(self):
        self.config = Config()
        self.config.validate()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
    
    def question_to_sql(self, question: str, schema: str, training_context: list = None) -> str:
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
        
        # Get training context if not provided
        if training_context is None:
            from backend.feedback_service import FeedbackService
            feedback_service = FeedbackService()
            training_context = feedback_service.get_semantic_context(question)
        
        # Build training context string
        context_str = ""
        if training_context:
            context_str = "\n\nTRAINING CONTEXT (use this to improve query generation):\n"
            for ctx in training_context[:3]:  # Use top 3 relevant contexts
                context_str += f"- Q: {ctx['question']}\n  A: {ctx['answer']}\n"
                if ctx.get('context'):
                    context_str += f"  Context: {ctx['context']}\n"
        
        # Regular data queries
        prompt = f"""
Generate MySQL query using the exact schema provided.

Schema: {schema}
Question: {question}{context_str}

CRITICAL TABLE AND COLUMN MAPPING:

TRADE_NEW table has: trade_id, notional_usd, batch_mtm, as_of_date, reporting_counterparty_id
COUNTERPARTY_NEW table has: counterparty_id, counterparty_sector, counterparty_name, mpe, mpe_limit
CONCENTRATION_NEW table has: counterparty_count, concentration_group, entity

IMPORTANT RULES:
- MPE (Market Price Exposure) is ONLY in counterparty_new table.
- Use MPE filters (mpe IS NOT NULL AND mpe != '' AND mpe != '0') **ONLY** for MPE-related questions.
- For exposure or trade-related questions (e.g., total notional, sector exposure, trade count), DO NOT apply MPE filters.
- counterparty_sector is ONLY in counterparty_new table.
- counterparty_count is ONLY in concentration_new table.
- For CCR portfolio exposure questions, use mpe from counterparty_new.

Use correct aliases: 
t = trade_new, c = counterparty_new, con = concentration_new

### Examples of correct usage (follow these patterns):

-- Sector analysis:
SELECT c.counterparty_sector, COUNT(t.trade_id) AS trade_count
FROM trade_new t
JOIN counterparty_new c ON t.reporting_counterparty_id = c.counterparty_id
GROUP BY c.counterparty_sector;

-- Concentration group analysis:
SELECT con.concentration_group, SUM(CAST(con.counterparty_count AS UNSIGNED)) AS total_count
FROM concentration_new con
GROUP BY con.concentration_group;

-- Monthly trend:
SELECT DATE_FORMAT(as_of_date, '%Y-%m') AS month,
       SUM(CAST(notional_usd AS DECIMAL(15,2))) AS monthly_notional
FROM trade_new
WHERE YEAR(as_of_date) = 2024
GROUP BY month
ORDER BY month;

-- MPE analysis:
SELECT DATE_FORMAT(as_of_date, '%Y-%m') AS month,
       SUM(CAST(mpe AS DECIMAL(15,2))) AS total_mpe
FROM counterparty_new
WHERE as_of_date LIKE '2024%'
  AND mpe IS NOT NULL
  AND mpe != ''
  AND mpe != '0'
GROUP BY month
ORDER BY month;

### MANDATORY JOIN PATTERNS (ALWAYS use these exact patterns):

-- For counterparty-trade relationships:
SELECT * FROM counterparty_new, trade_new 
WHERE counterparty_new.entity = trade_new.entity 
  AND counterparty_new.counterparty_id = trade_new.reporting_counterparty_id
LIMIT 10;

-- For counterparty-concentration by COUNTRY (REQUIRED pattern):
SELECT * FROM counterparty_new, concentration_new 
WHERE counterparty_new.entity = concentration_new.entity 
  AND counterparty_new.counterparty_country = concentration_new.concentration_value
LIMIT 10;

-- For counterparty-concentration by RATING (REQUIRED pattern):
SELECT * FROM counterparty_new, concentration_new 
WHERE counterparty_new.entity = concentration_new.entity 
  AND counterparty_new.internal_rating = concentration_new.concentration_value
LIMIT 10;

-- For counterparty-concentration by SECTOR (REQUIRED pattern):
SELECT * FROM counterparty_new, concentration_new 
WHERE counterparty_new.entity = concentration_new.entity 
  AND counterparty_new.counterparty_sector = concentration_new.concentration_value
LIMIT 10;

CRITICAL: When joining counterparty_new with concentration_new:
- ALWAYS use: counterparty_new.entity = concentration_new.entity
- PLUS one of these specific conditions:
  * counterparty_new.counterparty_country = concentration_new.concentration_value (for country analysis)
  * counterparty_new.internal_rating = concentration_new.concentration_value (for rating analysis)  
  * counterparty_new.counterparty_sector = concentration_new.concentration_value (for sector analysis)
- DO NOT use standard JOIN syntax - use WHERE clause with comma-separated tables


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
            cleaned_sql = self._clean_sql_output(sql_query)
            
            # Validate and fix forbidden functions
            if any(forbidden in cleaned_sql.upper() for forbidden in ['LAG', 'LEAD', 'OVER', 'WINDOW']):
                # Generate simpler query for MPE questions
                if 'mpe' in question.lower() or 'ccr' in question.lower():
                    return "SELECT DATE_FORMAT(as_of_date, '%Y-%m') AS month, SUM(CAST(mpe AS DECIMAL(15,2))) AS total_mpe, counterparty_sector FROM counterparty_new WHERE as_of_date LIKE '2024%' AND mpe IS NOT NULL AND mpe != '' AND mpe != '0' GROUP BY month, counterparty_sector ORDER BY month;"
                else:
                    return "SELECT counterparty_sector, COUNT(*) as count FROM counterparty_new GROUP BY counterparty_sector;"
            
            return cleaned_sql
            
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
            
            interpretation = json.loads(content)
            
            # Add Intent array
            interpretation["intent_array"] = self.generate_intent_array(question)
            
            return interpretation
            
        except Exception as e:
            # Fallback structure for any parsing errors
            return {
                "data_requested": f"Analysis of: {question}",
                "analysis_type": "Data query and analysis", 
                "context_significance": "Provides business insights from database",
                "intent_array": self.generate_intent_array(question)
            }
    
    def generate_intent_array(self, question: str) -> list:
        """Generate flattened Intent array representation from NLQ"""
        prompt = f"""
Analyze this natural language question and extract structured intent as a flattened array.

Question: {question}

Extract intent components and return as a JSON array of strings in this format:
[
  "entity: [entity_type]",
  "id: [specific_identifier]", 
  "metrics: [requested_metric]",
  "slice.as_of: [date_filter]",
  "slice.scenario: [scenario_type]"
]

Rules:
- entity: Main data entity (Counterparty, Trade, Portfolio, etc.)
- id: Specific identifier if mentioned (counterparty name, trade ID, etc.)
- metrics: What metric is requested (EAD, Notional, MPE, Count, etc.)
- slice.as_of: Date/time filter if specified
- slice.scenario: Scenario type (BASELINE, STRESS, etc.) - default to BASELINE
- Only include components that are present in the question
- Use UPPERCASE for identifiers and metrics
- Convert dates to YYYY-MM-DD format

Return only the JSON array:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=150
            )
            
            import json
            content = response.choices[0].message.content.strip()
            # Clean up any markdown formatting
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(content)
            
        except Exception as e:
            # Fallback intent array
            return [
                "entity: Data",
                "metrics: ANALYSIS"
            ]
    
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

    def export_training_data_to_jsonl(self, mysql_config: dict, table_name: str, 
                                  output_file: str = "training_data.jsonl", schema_cache=None):
    # """
    # Export MySQL table data into fine-tuning JSONL format.
    # If schema_cache is provided, use cached schema for all prompts.
    # """
        import pymysql
        conn = None
        try:
            conn = pymysql.connect(**mysql_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            if not rows:
                raise Exception("No training data found in table.")

            with open(output_file, "w", encoding="utf-8") as f:
                for row in rows:
                    schema_text = schema_cache.load_schema_from_cache() if schema_cache else "Schema not provided"
                    prompt = f"Generate SQL for this question using schema:\nSchema: {schema_text}\nQuestion: {row['question']}\nSQL:"
                    completion = row["answer"].strip() + " \ncontext : " + (row.get("context") or "")
                    
                    json.dump({"messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": completion}]}, f)
                    f.write("\n")

            return f"✅ Exported {len(rows)} training records to {output_file}"

        except Exception as e:
            raise Exception(f"Error exporting training data: {e}")
        finally:
            if conn:
                conn.close()
    
    def start_finetune_training(self, base_model: str = "gpt-4o-mini", training_file_path: str = "training_data.jsonl"):
        # """
        # Upload dataset and start fine-tuning job.
        # """
        try:
            # Upload file to OpenAI
            upload_response = self.client.files.create(
                file=open(training_file_path, "rb"),
                purpose="fine-tune"
            )

            file_id = upload_response.id
            print(f"✅ Uploaded training file: {file_id}")

            # Start fine-tune job
            fine_tune = self.client.fine_tuning.jobs.create(
                training_file=file_id,
                model=base_model,
            )

            job_id = fine_tune.id
            print(f"🚀 Fine-tuning started: {job_id}")

            return {
                "status": "started",
                "file_id": file_id,
                "job_id": job_id,
                "base_model": base_model
            }

        except Exception as e:
            raise Exception(f"Error starting fine-tune training: {e}")