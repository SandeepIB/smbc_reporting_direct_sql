import React, { useState } from 'react';
import './FeedbackSection.css';

const FeedbackSection = ({ message, onFeedback }) => {
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [feedbackType, setFeedbackType] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleThumbsClick = (type) => {
    setFeedbackType(type);
    if (type === 'down') {
      setShowFeedbackForm(true);
    } else {
      submitFeedback(type, '');
    }
  };

  const submitFeedback = async (type, text) => {
    setIsSubmitting(true);
    try {
      await onFeedback({
        messageId: message.id,
        type: type,
        feedback: text,
        originalQuery: message.originalQuestion,
        sqlQuery: message.sqlQuery,
        response: message.text
      });
      setShowFeedbackForm(false);
      setFeedbackText('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitFeedback = () => {
    if (feedbackText.trim()) {
      submitFeedback(feedbackType, feedbackText);
    }
  };

  if (message.sender !== 'bot' || !message.success || message.needsConfirmation || 
      message.text.includes('Thank you for the positive feedback') || 
      message.text.includes('Thank you for your feedback! I\'ve logged it for training')) return null;

  return (
    <div className="feedback-section">
      <div className="feedback-buttons">
        <button 
          className={`feedback-btn thumbs-up ${feedbackType === 'up' ? 'selected' : ''}`}
          onClick={() => handleThumbsClick('up')}
          title="Good response"
        >
          👍
        </button>
        <button 
          className={`feedback-btn thumbs-down ${feedbackType === 'down' ? 'selected' : ''}`}
          onClick={() => handleThumbsClick('down')}
          title="Needs improvement"
        >
          👎
        </button>
      </div>

      {showFeedbackForm && (
        <div className="feedback-form">
          <p className="feedback-prompt">How can we improve this response?</p>
          <textarea
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="e.g., Use exposure net of collateral, Include more recent data..."
            className="feedback-input"
            rows="3"
          />
          <div className="feedback-actions">
            <button 
              onClick={handleSubmitFeedback}
              disabled={!feedbackText.trim() || isSubmitting}
              className="submit-feedback-btn"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
            <button 
              onClick={() => setShowFeedbackForm(false)}
              className="cancel-feedback-btn"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackSection;