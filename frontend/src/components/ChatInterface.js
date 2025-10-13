import React, { useState, useRef, useEffect } from 'react';
import FeedbackSection from './FeedbackSection';
import './ChatInterface.css';

// Info icon component (unused but kept for future use)
// const InfoIcon = ({ onClick, isExpanded }) => (
//   <button
//     onClick={onClick}
//     className={`ml-2 p-1 rounded-full hover:bg-gray-100 transition-colors ${
//       isExpanded ? 'bg-gray-100' : ''
//     }`}
//     title="Show SQL query and raw data"
//   >
//     <svg
//       width="16"
//       height="16"
//       viewBox="0 0 24 24"
//       fill="none"
//       className="text-gray-500 hover:text-gray-700"
//     >
//       <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
//       <path d="M9,9h0a3,3,0,0,1,6,0c0,2-3,3-3,3" stroke="currentColor" strokeWidth="2" />
//       <path d="M12,17h0" stroke="currentColor" strokeWidth="2" />
//     </svg>
//   </button>
// );

// Edit Question component
const EditQuestionSection = ({ originalQuestion, onEditSubmit, onCancel }) => {
  const [editedQuestion, setEditedQuestion] = useState(originalQuestion);
  
  const handleSubmit = () => {
    if (editedQuestion.trim() && editedQuestion !== originalQuestion) {
      onEditSubmit(editedQuestion);
    }
  };
  
  return (
    <div className="edit-question-section">
      <div className="edit-question-header">
        <svg className="edit-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        <h3 className="edit-question-title">Edit Your Question</h3>
      </div>
      
      <textarea
        value={editedQuestion}
        onChange={(e) => setEditedQuestion(e.target.value)}
        className="edit-question-textarea"
        rows="3"
        placeholder="Edit your question here..."
      />
      
      <div className="edit-question-buttons">
        <button
          onClick={handleSubmit}
          disabled={!editedQuestion.trim() || editedQuestion === originalQuestion}
          className="edit-submit-btn"
        >
          <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          Submit Edited Question
        </button>
        <button
          onClick={onCancel}
          className="edit-cancel-btn"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

// Confirmation component
const ConfirmationSection = ({ message, onConfirm, onEditQuestion, isConfirming }) => {
  const interpretation = message.interpretedQuestion;
  
  return (
    <div className="confirmation-section">
      <div className="confirmation-title">Please confirm your question:</div>
      <p>The question <strong>"{message.originalQuestion}"</strong> can be interpreted as follows:</p>
      
      <div className="interpretation-details">
        <h4>Data requested:</h4>
        <p>{interpretation?.data_requested || 'Data analysis'}</p>
        
        <h4>Analysis type:</h4>
        <p>{interpretation?.analysis_type || 'Query analysis'}</p>
        
        <h4>Context:</h4>
        <p>{interpretation?.context_significance || 'Provides business insights'}</p>
        
        {interpretation?.intent_array && interpretation.intent_array.length > 0 && (
          <div>
            <h4>Intent (Array Form):</h4>
            <pre>
{`[
${interpretation.intent_array.map(item => `  "${item}"`).join(',\n')}
]`}
            </pre>
          </div>
        )}
      </div>
      
      <p><strong>Do you want me to proceed with this interpretation?</strong></p>
      
      <div className="confirmation-buttons">
        <button
          onClick={() => onConfirm(true)}
          disabled={isConfirming}
          className="confirm-btn"
        >
          {isConfirming ? 'Processing...' : 'Yes, correct'}
        </button>
        <button
          onClick={onEditQuestion}
          disabled={isConfirming}
          className="cancel-btn"
        >
          No, let me rephrase
        </button>
      </div>
    </div>
  );
};

// Refinement component
const RefinementSection = ({ message, onRefine, isRefining }) => {
  const [showRefineInput, setShowRefineInput] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleRefine = () => {
    if (feedback.trim()) {
      onRefine(message.originalQuestion || message.text, feedback);
      setFeedback('');
      setShowRefineInput(false);
    }
  };

  return (
    <div className="refinement-section">
      <div className="refinement-header">
        <span className="refinement-icon">💡</span>
        <span className="refinement-title">Refine the question?</span>
      </div>
      
      {!showRefineInput ? (
        <div className="refinement-initial-buttons">
          <button
            onClick={() => setShowRefineInput(true)}
            className="refinement-yes-btn"
          >
            Yes
          </button>
          <button
            onClick={() => {/* Hide refinement section */}}
            className="refinement-no-btn"
          >
            No
          </button>
        </div>
      ) : (
        <div className="refinement-input-area">
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="How would you like me to refine or reframe the question?"
            className="refinement-textarea"
            rows="2"
          />
          <div className="refinement-action-buttons">
            <button
              onClick={handleRefine}
              disabled={!feedback.trim() || isRefining}
              className="refinement-submit-btn"
            >
              {isRefining ? 'Refining...' : 'Refine'}
            </button>
            <button
              onClick={() => setShowRefineInput(false)}
              className="refinement-cancel-btn"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Download report component
const DownloadReportSection = ({ message, onDownloadReport, isGenerating }) => {
  if (!message.sqlQuery || !message.rawData) return null;
  
  return (
    <div className="download-report-section">
      <div className="download-report-content">
        <div className="download-report-info">
          <svg className="download-report-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="download-report-text">Executive Report Available</span>
        </div>
        <button
          onClick={() => onDownloadReport(message)}
          disabled={isGenerating}
          className="download-report-btn"
        >
          <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
          {isGenerating ? 'Generating...' : 'Download Report'}
        </button>
      </div>
    </div>
  );
};

// Expandable details component
const MessageDetails = ({ sqlQuery, rawData, rowCount, dataSources, isExpanded }) => {
  if (!isExpanded) return null;

  return (
    <div className="message-details">
      <div className="message-details-content">
        {/* Data Sources Section */}
        {dataSources && dataSources.length > 0 && (
          <div className="data-sources-section">
            <h4 className="section-title">Data Sources:</h4>
            <div className="data-sources-list">
              <ul className="sources-list">
                {dataSources.map((source, index) => (
                  <li key={index} className="source-item">
                    <svg className="source-icon" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm8 0a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1V8z" clipRule="evenodd" />
                    </svg>
                    {source}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        {/* SQL Query Section */}
        <div className="sql-section">
          <h4 className="section-title">SQL Query:</h4>
          <div className="sql-code-block">
            <pre className="sql-code">{sqlQuery}</pre>
          </div>
        </div>

        {/* Raw Data Section */}
        <div className="raw-data-section">
          <h4 className="section-title">
            Raw Data ({rowCount} rows):
          </h4>
          <div className="data-table-container">
            {rawData && rawData.length > 0 ? (
              <div className="table-wrapper">
                <table className="data-table">
                  <thead className="table-header">
                    <tr>
                      {Object.keys(rawData[0]).map((key) => (
                        <th key={key} className="table-header-cell">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rawData.slice(0, 10).map((row, index) => (
                      <tr key={index} className="table-row">
                        {Object.values(row).map((value, cellIndex) => (
                          <td key={cellIndex} className="table-cell">
                            {value !== null && value !== undefined ? String(value) : 'NULL'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {rawData.length > 10 && (
                  <div className="table-footer">
                    ... and {rawData.length - 10} more rows
                  </div>
                )}
              </div>
            ) : (
              <div className="no-data-message">No data returned</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const ChatInterface = ({ messages, onSendMessage, onConfirmQuestion, onRefineMessage, onDownloadReport, onFeedback, isLoading, hideHeader = false }) => {
  const [inputValue, setInputValue] = useState('');
  const [expandedMessages, setExpandedMessages] = useState(new Set());
  const [isRefining, setIsRefining] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [editingMessageId, setEditingMessageId] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const toggleMessageDetails = (messageId) => {
    const newExpanded = new Set(expandedMessages);
    if (newExpanded.has(messageId)) {
      newExpanded.delete(messageId);
    } else {
      newExpanded.add(messageId);
    }
    setExpandedMessages(newExpanded);
  };

  const handleConfirmQuestion = async (confirmed) => {
    setIsConfirming(true);
    try {
      await onConfirmQuestion(confirmed);
    } finally {
      setIsConfirming(false);
    }
  };

  const handleRefineMessage = async (originalQuestion, feedback) => {
    setIsRefining(true);
    try {
      await onRefineMessage(originalQuestion, feedback);
    } finally {
      setIsRefining(false);
    }
  };

  const handleDownloadReport = async (message) => {
    setIsGeneratingReport(true);
    try {
      await onDownloadReport(message);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const handleEditQuestion = (messageId) => {
    setEditingMessageId(messageId);
  };

  const handleEditSubmit = (editedQuestion) => {
    // Clear the editing state first
    setEditingMessageId(null);
    // Send the edited question directly
    onSendMessage(editedQuestion);
  };

  const handleEditCancel = () => {
    setEditingMessageId(null);
  };

  const handlePrePrompt = (prompt) => {
    setInputValue(prompt);
    inputRef.current?.focus();
  };

  const prePrompts = [
    "Top 5 counterparties with highest credit exposure",
    "Top major movers in the last 3 months", 
    "Key credit risk concentrations by MPE"
  ];

  return (
    <div className={`chat-interface ${hideHeader ? '' : 'full-height'}`}>
      {/* Messages Area */}
      <div className="messages-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to Counterparty Risk Assistant</h2>
              <p>Ask me anything about counterparty credit risk.</p>
              
              <div className="pre-prompts">
                <h3>Quick Start Questions:</h3>
                <div className="pre-prompt-cards">
                  {prePrompts.map((prompt, index) => (
                    <button
                      key={index}
                      className="pre-prompt-card"
                      onClick={() => handlePrePrompt(prompt)}
                      disabled={isLoading}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-content">
                <div className="message-text">{message.text}</div>
                
                {message.sender === 'bot' && message.sqlQuery && (
                  <MessageDetails
                    sqlQuery={message.sqlQuery}
                    rawData={message.rawData}
                    rowCount={message.rowCount}
                    dataSources={message.dataSources}
                    isExpanded={expandedMessages.has(message.id)}
                  />
                )}
                
                {message.sender === 'bot' && message.success && message.sqlQuery && (
                  <div>
                    <button
                      onClick={() => toggleMessageDetails(message.id)}
                      className="expand-results-btn-right"
                    >
                      {expandedMessages.has(message.id) ? 'Collapse results' : 'Expand results'}
                      <svg 
                        className={`expand-arrow ${expandedMessages.has(message.id) ? 'expanded' : ''}`}
                        width="16" 
                        height="16" 
                        viewBox="0 0 24 24" 
                        fill="none"
                      >
                        <path 
                          d="M6 9l6 6 6-6" 
                          stroke="currentColor" 
                          strokeWidth="2" 
                          strokeLinecap="round" 
                          strokeLinejoin="round"
                        />
                      </svg>
                    </button>
                    
                    <DownloadReportSection
                      message={message}
                      onDownloadReport={handleDownloadReport}
                      isGenerating={isGeneratingReport}
                    />
                  </div>
                )}
                
                {message.sender === 'bot' && message.needsConfirmation && editingMessageId !== message.id && (
                  <ConfirmationSection
                    message={message}
                    onConfirm={handleConfirmQuestion}
                    onEditQuestion={() => handleEditQuestion(message.id)}
                    isConfirming={isConfirming}
                  />
                )}
                
                {editingMessageId === message.id && (
                  <EditQuestionSection
                    originalQuestion={message.originalQuestion}
                    onEditSubmit={handleEditSubmit}
                    onCancel={handleEditCancel}
                  />
                )}
                
                {message.sender === 'bot' && message.needsRefinement && (
                  <RefinementSection
                    message={message}
                    onRefine={handleRefineMessage}
                    isRefining={isRefining}
                  />
                )}
                
                <FeedbackSection 
                  message={message} 
                  onFeedback={onFeedback}
                />
                
                <div className="message-time">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message bot">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-form">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask us anything..."
            className="message-input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={!inputValue.trim() || isLoading}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path 
                d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </form>
      </div>

    </div>
  );
};

export default ChatInterface;