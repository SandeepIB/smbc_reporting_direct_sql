import React, { useState, useRef, useEffect } from 'react';
import FeedbackSection from './FeedbackSection';
import config from '../config/api';
import './ChatInterface.css';

// Info icon component
const InfoIcon = ({ onClick, isExpanded }) => (
  <button
    onClick={onClick}
    className={`ml-2 p-1 rounded-full hover:bg-gray-100 transition-colors ${
      isExpanded ? 'bg-gray-100' : ''
    }`}
    title="Show SQL query and raw data"
  >
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      className="text-gray-500 hover:text-gray-700"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
      <path d="M9,9h0a3,3,0,0,1,6,0c0,2-3,3-3,3" stroke="currentColor" strokeWidth="2" />
      <path d="M12,17h0" stroke="currentColor" strokeWidth="2" />
    </svg>
  </button>
);

// Edit Question component
const EditQuestionSection = ({ originalQuestion, onEditSubmit, onCancel }) => {
  const [editedQuestion, setEditedQuestion] = useState(originalQuestion);
  
  const handleSubmit = () => {
    if (editedQuestion.trim() && editedQuestion !== originalQuestion) {
      onEditSubmit(editedQuestion);
    }
  };
  
  return (
    <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
      <div className="flex items-center gap-2 mb-3">
        <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        <h3 className="text-base font-semibold text-yellow-800">Edit Your Question</h3>
      </div>
      
      <textarea
        value={editedQuestion}
        onChange={(e) => setEditedQuestion(e.target.value)}
        className="w-full p-3 border border-yellow-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-yellow-500"
        rows="3"
        placeholder="Edit your question here..."
      />
      
      <div className="flex gap-3 mt-3">
        <button
          onClick={handleSubmit}
          disabled={!editedQuestion.trim() || editedQuestion === originalQuestion}
          className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          Submit Edited Question
        </button>
        <button
          onClick={onCancel}
          className="inline-flex items-center gap-2 px-4 py-2 bg-gray-500 text-white text-sm font-medium rounded-lg hover:bg-gray-600 transition-colors"
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
    <div className="mt-4 p-5 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-xl border border-blue-200 shadow-lg">
      <div className="flex items-start gap-4 mb-5">
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-md">
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-base font-semibold text-gray-800 mb-2">Please confirm your question:</h3>
          <p className="text-sm text-gray-600 mb-4 leading-relaxed">
            The question <span className="font-medium text-gray-800 bg-white px-2 py-1 rounded border">"{message.originalQuestion}"</span> can be interpreted as follows:
          </p>
          
          <div className="space-y-3 mb-5">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm8 0a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1V8z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Data requested:</p>
                <p className="text-sm text-gray-600">{interpretation?.data_requested || 'Data analysis'}</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Analysis type:</p>
                <p className="text-sm text-gray-600">{interpretation?.analysis_type || 'Query analysis'}</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center">
                <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Context:</p>
                <p className="text-sm text-gray-600">{interpretation?.context_significance || 'Provides business insights'}</p>
              </div>
            </div>
          </div>
          
          {/* Intent Array Section */}
          {interpretation?.intent_array && interpretation.intent_array.length > 0 && (
            <div className="mt-4 p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg border border-indigo-200">
              <div className="flex items-center gap-2 mb-3">
                <div className="flex-shrink-0 w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm8 0a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1V8z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-sm font-medium text-gray-700">Intent (Array Form):</p>
              </div>
              <div className="bg-gray-900 text-green-400 p-3 rounded-lg text-sm font-mono overflow-x-auto">
                <pre className="whitespace-pre-wrap">
{`[
${interpretation.intent_array.map(item => `  "${item}"`).join(',\n')}
]`}
                </pre>
              </div>
            </div>
          )}
          
          <p className="text-sm font-medium text-gray-700 mb-4">Do you want me to proceed with this interpretation?</p>
        </div>
      </div>
      
      <div className="flex gap-3">
        <button
          onClick={() => onConfirm(true)}
          disabled={isConfirming}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-green-600 to-green-700 text-white text-sm font-medium rounded-lg hover:from-green-700 hover:to-green-800 disabled:opacity-50 transition-all duration-200 shadow-md hover:shadow-lg"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {isConfirming ? 'Processing...' : 'Yes, correct'}
        </button>
        <button
          onClick={onEditQuestion}
          disabled={isConfirming}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-gray-600 to-gray-700 text-white text-sm font-medium rounded-lg hover:from-gray-700 hover:to-gray-800 disabled:opacity-50 transition-all duration-200 shadow-md hover:shadow-lg"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
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
    <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">💡</span>
        <span className="text-sm font-medium text-blue-800">Refine the question?</span>
      </div>
      
      {!showRefineInput ? (
        <div className="flex gap-2">
          <button
            onClick={() => setShowRefineInput(true)}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
          >
            Yes
          </button>
          <button
            onClick={() => {/* Hide refinement section */}}
            className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded hover:bg-gray-400 transition-colors"
          >
            No
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="How would you like me to refine or reframe the question?"
            className="w-full p-2 text-sm border border-gray-300 rounded resize-none"
            rows="2"
          />
          <div className="flex gap-2">
            <button
              onClick={handleRefine}
              disabled={!feedback.trim() || isRefining}
              className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isRefining ? 'Refining...' : 'Refine'}
            </button>
            <button
              onClick={() => setShowRefineInput(false)}
              className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded hover:bg-gray-400 transition-colors"
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
    <div className="mt-3 p-3 bg-green-50 rounded-lg border border-green-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="text-sm font-medium text-green-800">Executive Report Available</span>
        </div>
        <button
          onClick={() => onDownloadReport(message)}
          disabled={isGenerating}
          className="inline-flex items-center gap-2 px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
      <div className="space-y-3">
        {/* Data Sources Section */}
        {dataSources && dataSources.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Data Sources:</h4>
            <div className="bg-green-50 p-3 rounded border border-green-200">
              <ul className="text-sm text-gray-700 space-y-1">
                {dataSources.map((source, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
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
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">SQL Query:</h4>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm font-mono overflow-x-auto border border-gray-700">
            <pre className="whitespace-pre-wrap leading-relaxed">{sqlQuery}</pre>
          </div>
        </div>

        {/* Raw Data Section */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">
            Raw Data ({rowCount} rows):
          </h4>
          <div className="bg-white border rounded max-h-64 overflow-auto">
            {rawData && rawData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(rawData[0]).map((key) => (
                        <th key={key} className="px-3 py-2 text-left font-medium text-gray-700 border-b">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rawData.slice(0, 10).map((row, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        {Object.values(row).map((value, cellIndex) => (
                          <td key={cellIndex} className="px-3 py-2 border-b text-gray-600">
                            {value !== null && value !== undefined ? String(value) : 'NULL'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {rawData.length > 10 && (
                  <div className="p-2 text-center text-gray-500 text-sm border-t">
                    ... and {rawData.length - 10} more rows
                  </div>
                )}
              </div>
            ) : (
              <div className="p-4 text-center text-gray-500">No data returned</div>
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
      {/* Header */}
      {!hideHeader && (
        <div className="chat-header">
          <div className="header-content">
            <div className="logo">
              <div className="logo-icon">🔍</div>
              <span className="logo-text">Counterparty Risk Assistant</span>
            </div>
          </div>
        </div>
      )}

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