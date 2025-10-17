# src/services/retriever.py

from backend.feedback_service import FeedbackService

def retrieve(question: str, k: int = 5):
    """
    Retrieve top-k relevant context for a question.
    Uses FeedbackService semantic search as RAG source.
    """
    try:
        feedback_service = FeedbackService()
        context = feedback_service.get_semantic_context(question)[:k]
        # Ensure format matches RAG style
        results = []
        for ctx in context:
            results.append({
                "question": ctx.get("question", ""),
                "answer": ctx.get("answer", ""),
                "context": ctx.get("context", "")
            })
        return results
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return []
