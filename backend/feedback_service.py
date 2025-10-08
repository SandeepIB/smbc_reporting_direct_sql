import json
import mysql.connector
from datetime import datetime
from typing import List, Dict, Any
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE', 'org_insights')
        }
        self.init_database()
    
    def init_database(self):
        """Initialize the feedback database"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message_id VARCHAR(255),
                type VARCHAR(50),
                feedback TEXT,
                original_query TEXT,
                sql_query TEXT,
                response TEXT,
                session_id VARCHAR(255),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create training data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT,
                answer TEXT,
                context TEXT,
                source VARCHAR(50) DEFAULT 'manual',
                approved_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def submit_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit user feedback"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (message_id, type, feedback, original_query, sql_query, response, session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            feedback_data.get('messageId'),
            feedback_data.get('type'),
            feedback_data.get('feedback', ''),
            feedback_data.get('originalQuery'),
            feedback_data.get('sqlQuery'),
            feedback_data.get('response'),
            feedback_data.get('sessionId')
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Feedback submitted: {feedback_id}")
        return {"id": feedback_id, "status": "submitted"}
    
    def get_pending_feedbacks(self) -> List[Dict[str, Any]]:
        """Get all pending feedbacks for admin review"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, message_id, type, feedback, original_query, sql_query, response, created_at
            FROM feedback 
            WHERE status = 'pending' AND type = 'down'
            ORDER BY created_at DESC
        ''')
        
        feedbacks = []
        for row in cursor.fetchall():
            feedbacks.append({
                'id': row[0],
                'message_id': row[1],
                'type': row[2],
                'feedback': row[3],
                'original_query': row[4],
                'sql_query': row[5],
                'response': row[6],
                'created_at': row[7].isoformat() if row[7] else None
            })
        
        conn.close()
        return feedbacks
    
    def approve_feedback(self, feedback_id: int) -> Dict[str, Any]:
        """Approve feedback and add to training data"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Get feedback details
        cursor.execute('SELECT * FROM feedback WHERE id = %s', (feedback_id,))
        feedback = cursor.fetchone()
        
        if not feedback:
            conn.close()
            raise ValueError("Feedback not found")
        
        # Add to training data
        cursor.execute('''
            INSERT INTO training_data (question, answer, context, source, approved_by)
            VALUES (%s, %s, %s, 'feedback', 'admin')
        ''', (
            feedback[4],  # original_query
            f"User feedback: {feedback[3]}",  # feedback as answer
            f"Original response: {feedback[6]}"  # response as context
        ))
        
        # Update feedback status
        cursor.execute('UPDATE feedback SET status = %s WHERE id = %s', ('approved', feedback_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Feedback approved and added to training: {feedback_id}")
        return {"status": "approved"}
    
    def reject_feedback(self, feedback_id: int) -> Dict[str, Any]:
        """Reject feedback"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE feedback SET status = %s WHERE id = %s', ('rejected', feedback_id))
        conn.commit()
        conn.close()
        
        logger.info(f"Feedback rejected: {feedback_id}")
        return {"status": "rejected"}
    
    def get_training_data(self) -> List[Dict[str, Any]]:
        """Get all training data"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question, answer, context, source, created_at
            FROM training_data 
            ORDER BY created_at DESC
        ''')
        
        training_data = []
        for row in cursor.fetchall():
            training_data.append({
                'id': row[0],
                'question': row[1],
                'answer': row[2],
                'context': row[3],
                'source': row[4],
                'created_at': row[5].isoformat() if row[5] else None
            })
        
        conn.close()
        return training_data
    
    def add_training_data(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add new training data"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_data (question, answer, context, source, approved_by)
            VALUES (%s, %s, %s, 'manual', 'admin')
        ''', (
            training_data.get('question'),
            training_data.get('answer'),
            training_data.get('context', '')
        ))
        
        training_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Training data added: {training_id}")
        return {"id": training_id, "status": "added"}
    
    def get_semantic_context(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant training data for semantic enhancement"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Simple keyword matching - in production, use vector similarity
        keywords = query.lower().split()
        
        cursor.execute('''
            SELECT question, answer, context FROM training_data 
            WHERE question LIKE %s OR answer LIKE %s
            LIMIT 5
        ''', (f'%{" ".join(keywords[:3])}%', f'%{" ".join(keywords[:3])}%'))
        
        context = []
        for row in cursor.fetchall():
            context.append({
                'question': row[0],
                'answer': row[1],
                'context': row[2]
            })
        
        conn.close()
        return context
    
    def get_all_feedbacks(self) -> List[Dict[str, Any]]:
        """Get all feedbacks for admin review"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, message_id, type, feedback, original_query, sql_query, response, status, created_at
            FROM feedback 
            ORDER BY created_at DESC
        ''')
        
        feedbacks = []
        for row in cursor.fetchall():
            feedbacks.append({
                'id': row[0],
                'message_id': row[1],
                'type': row[2],
                'feedback': row[3],
                'original_query': row[4],
                'sql_query': row[5],
                'response': row[6],
                'status': row[7],
                'created_at': row[8].isoformat() if row[8] else None
            })
        
        conn.close()
        return feedbacks
    
    def create_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new feedback"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (message_id, type, feedback, original_query, sql_query, response, session_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            f"admin-{datetime.now().timestamp()}",
            feedback_data.get('type', 'manual'),
            feedback_data.get('feedback'),
            feedback_data.get('original_query'),
            feedback_data.get('sql_query'),
            feedback_data.get('response'),
            'admin-session',
            'pending'
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Feedback created by admin: {feedback_id}")
        return {"id": feedback_id, "status": "created"}
    
    def update_feedback(self, feedback_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing feedback"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        for field, value in update_data.items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)
        
        if not update_fields:
            raise ValueError("No fields to update")
        
        update_values.append(feedback_id)
        
        cursor.execute(f'''
            UPDATE feedback 
            SET {', '.join(update_fields)}
            WHERE id = %s
        ''', update_values)
        
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError("Feedback not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Feedback updated: {feedback_id}")
        return {"status": "updated"}
    
    def delete_feedback(self, feedback_id: int) -> Dict[str, Any]:
        """Delete feedback"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM feedback WHERE id = %s', (feedback_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError("Feedback not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Feedback deleted: {feedback_id}")
        return {"status": "deleted"}