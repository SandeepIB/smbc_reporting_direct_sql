import React, { useState, useEffect } from 'react';
import { chatService } from '../services/chatService';
import './AdminInterface.css';

const AdminInterface = () => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [allFeedbacks, setAllFeedbacks] = useState([]);
  const [trainingData, setTrainingData] = useState([]);
  const [newTraining, setNewTraining] = useState({ question: '', answer: '', context: '' });
  const [newFeedback, setNewFeedback] = useState({ original_query: '', feedback: '', sql_query: '', response: '' });
  // const [editingFeedback, setEditingFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('pending');
  const [showAddTrainingModal, setShowAddTrainingModal] = useState(false);
  const [showAddFeedbackModal, setShowAddFeedbackModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(8);

  useEffect(() => {
    console.log('AdminInterface mounted, loading data...');
    loadFeedbacks();
    loadAllFeedbacks();
    loadTrainingData();
  }, []);



  const loadFeedbacks = async () => {
    try {
      const data = await chatService.getPendingFeedbacks();
      setFeedbacks(data);
    } catch (error) {
      console.error('Error loading feedbacks:', error);
    }
  };

  const loadAllFeedbacks = async () => {
    try {
      console.log('Loading all feedbacks...');
      const data = await chatService.getAllFeedbacks();
      console.log('All feedbacks loaded:', data);
      setAllFeedbacks(data || []);
    } catch (error) {
      console.error('Error loading all feedbacks:', error);
      setAllFeedbacks([]);
    }
  };

  const loadTrainingData = async () => {
    try {
      console.log('Loading training data...');
      const data = await chatService.getTrainingData();
      console.log('Training data loaded:', data);
      setTrainingData(data || []);
    } catch (error) {
      console.error('Error loading training data:', error);
      setTrainingData([]);
    }
  };

  const approveFeedback = async (feedbackId) => {
    setLoading(true);
    try {
      await chatService.approveFeedback(feedbackId);
      await loadFeedbacks();
      await loadAllFeedbacks();
      await loadTrainingData();
    } catch (error) {
      console.error('Error approving feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const rejectFeedback = async (feedbackId) => {
    setLoading(true);
    try {
      await chatService.rejectFeedback(feedbackId);
      await loadFeedbacks();
      await loadAllFeedbacks();
    } catch (error) {
      console.error('Error rejecting feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const createFeedback = async () => {
    if (!newFeedback.original_query.trim() || !newFeedback.feedback.trim()) return;
    
    setLoading(true);
    try {
      const result = await chatService.createFeedback(newFeedback);
      console.log('Feedback created:', result);
      setNewFeedback({ original_query: '', feedback: '', sql_query: '', response: '' });
      await loadAllFeedbacks();
      await loadFeedbacks();
    } catch (error) {
      console.error('Error creating feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  // const updateFeedback = async (feedbackId, updateData) => {
  //   setLoading(true);
  //   try {
  //     await chatService.updateFeedback(feedbackId, updateData);
  //     setEditingFeedback(null);
  //     await loadAllFeedbacks();
  //   } catch (error) {
  //     console.error('Error updating feedback:', error);
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  const deleteFeedback = async (feedbackId) => {
    if (!window.confirm('Are you sure you want to delete this feedback?')) return;
    
    setLoading(true);
    try {
      await chatService.deleteFeedback(feedbackId);
      await loadAllFeedbacks();
    } catch (error) {
      console.error('Error deleting feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const addTrainingData = async () => {
    if (!newTraining.question.trim() || !newTraining.answer.trim()) return;
    
    setLoading(true);
    try {
      const result = await chatService.addTrainingData(newTraining);
      console.log('Training data added:', result);
      setNewTraining({ question: '', answer: '', context: '' });
      await loadTrainingData();
    } catch (error) {
      console.error('Error adding training data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-interface">
      <div className="admin-header">
        <h2>Admin Dashboard</h2>
        <div className="admin-tabs">
          <button 
            className={`tab-btn ${activeTab === 'pending' ? 'active' : ''}`}
            onClick={() => setActiveTab('pending')}
          >
            📋 Pending ({feedbacks.length})
          </button>
          <button 
            className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            📊 All Feedback ({allFeedbacks.length})
          </button>
          <button 
            className={`tab-btn ${activeTab === 'training' ? 'active' : ''}`}
            onClick={() => setActiveTab('training')}
          >
            🎓 Training Data ({trainingData.length})
          </button>
          <button 
            className="tab-btn refresh-btn"
            onClick={() => {
              loadFeedbacks();
              loadAllFeedbacks();
              loadTrainingData();
            }}
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

        <div className="admin-content">
          
          {activeTab === 'pending' && (
          <div className="admin-section">
            <div className="section-header">
              <h3>Pending Feedback</h3>
              <button 
                className="add-btn"
                onClick={() => setShowAddFeedbackModal(true)}
              >
                ➕ Add Feedback
              </button>
            </div>
            
            <div className="table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Original Query</th>
                    <th>Feedback</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {feedbacks
                    .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                    .map(feedback => (
                    <tr key={feedback.id}>
                      <td>{feedback.id}</td>
                      <td className="text-cell">{feedback.original_query}</td>
                      <td className="text-cell">{feedback.feedback}</td>
                      <td>{new Date(feedback.created_at).toLocaleDateString()}</td>
                      <td>
                        <button 
                          onClick={() => approveFeedback(feedback.id)}
                          disabled={loading}
                          className="btn-approve"
                        >
                          ✓
                        </button>
                        <button 
                          onClick={() => rejectFeedback(feedback.id)}
                          disabled={loading}
                          className="btn-reject"
                        >
                          ✗
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {feedbacks.length === 0 && (
                <div className="empty-state">No pending feedback</div>
              )}
            </div>
            
            {feedbacks.length > itemsPerPage && (
              <div className="pagination">
                <button 
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="pagination-btn"
                >
                  Previous
                </button>
                
                <span className="pagination-info">
                  Page {currentPage} of {Math.ceil(feedbacks.length / itemsPerPage)}
                </span>
                
                <button 
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, Math.ceil(feedbacks.length / itemsPerPage)))}
                  disabled={currentPage === Math.ceil(feedbacks.length / itemsPerPage)}
                  className="pagination-btn"
                >
                  Next
                </button>
              </div>
            )}
          </div>
          )}

          {activeTab === 'all' && (
          <div className="admin-section">
            <div className="section-header">
              <h3>All Feedback</h3>
              <button 
                className="add-btn"
                onClick={() => setShowAddFeedbackModal(true)}
              >
                ➕ Add Feedback
              </button>
            </div>
            
            <div className="table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Original Query</th>
                    <th>Feedback</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {allFeedbacks.map(feedback => (
                    <tr key={feedback.id}>
                      <td>{feedback.id}</td>
                      <td>
                        <span className={`status-badge status-${feedback.status}`}>
                          {feedback.status}
                        </span>
                      </td>
                      <td className="text-cell">{feedback.original_query}</td>
                      <td className="text-cell">{feedback.feedback}</td>
                      <td>{new Date(feedback.created_at).toLocaleDateString()}</td>
                      <td>
                        {/* <button 
                          onClick={() => setEditingFeedback(feedback.id)}
                          className="btn-edit"
                        >
                          ✏️
                        </button> */}
                        <button 
                          onClick={() => deleteFeedback(feedback.id)}
                          disabled={loading}
                          className="btn-delete"
                        >
                          🗑️
                        </button>
                        {feedback.status === 'pending' && (
                          <>
                            <button 
                              onClick={() => approveFeedback(feedback.id)}
                              disabled={loading}
                              className="btn-approve"
                            >
                              ✓
                            </button>
                            <button 
                              onClick={() => rejectFeedback(feedback.id)}
                              disabled={loading}
                              className="btn-reject"
                            >
                              ✗
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {allFeedbacks.length === 0 && (
                <div className="empty-state">No feedback available</div>
              )}
            </div>
          </div>
          )}

          {activeTab === 'training' && (
          <div className="admin-section">
            <div className="section-header">
              <h3>Training Data</h3>
              <button 
                className="add-btn"
                onClick={() => setShowAddTrainingModal(true)}
              >
                ➕ Add Training Data
              </button>
            </div>
            
            <div className="table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Question</th>
                    <th>Answer</th>
                    <th>Source</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {trainingData.map(item => (
                    <tr key={item.id}>
                      <td>{item.id}</td>
                      <td className="text-cell">{item.question}</td>
                      <td className="text-cell">{item.answer}</td>
                      <td>
                        <span className="source-badge">{item.source}</span>
                      </td>
                      <td>{new Date(item.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {trainingData.length === 0 && (
                <div className="empty-state">No training data available</div>
              )}
            </div>
          </div>
          )}
        </div>
        
        {/* Add Training Data Modal */}
        {showAddTrainingModal && (
          <div className="modal-overlay" onClick={() => setShowAddTrainingModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Add Training Data</h3>
                <button 
                  className="modal-close"
                  onClick={() => setShowAddTrainingModal(false)}
                >
                  ✕
                </button>
              </div>
              <div className="modal-body">
                <textarea
                  placeholder="User question or prompt..."
                  value={newTraining.question}
                  onChange={(e) => setNewTraining({...newTraining, question: e.target.value})}
                  className="modal-input"
                  rows="3"
                />
                <textarea
                  placeholder="Expected answer or guidance..."
                  value={newTraining.answer}
                  onChange={(e) => setNewTraining({...newTraining, answer: e.target.value})}
                  className="modal-input"
                  rows="4"
                />
                <textarea
                  placeholder="Context or additional notes (optional)..."
                  value={newTraining.context}
                  onChange={(e) => setNewTraining({...newTraining, context: e.target.value})}
                  className="modal-input"
                  rows="2"
                />
              </div>
              <div className="modal-footer">
                <button 
                  onClick={() => setShowAddTrainingModal(false)}
                  className="btn-cancel"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => {
                    addTrainingData();
                    setShowAddTrainingModal(false);
                  }}
                  disabled={loading || !newTraining.question.trim() || !newTraining.answer.trim()}
                  className="btn-save"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Add Feedback Modal */}
        {showAddFeedbackModal && (
          <div className="modal-overlay" onClick={() => setShowAddFeedbackModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Add Feedback</h3>
                <button 
                  className="modal-close"
                  onClick={() => setShowAddFeedbackModal(false)}
                >
                  ✕
                </button>
              </div>
              <div className="modal-body">
                <textarea
                  placeholder="Original query..."
                  value={newFeedback.original_query}
                  onChange={(e) => setNewFeedback({...newFeedback, original_query: e.target.value})}
                  className="modal-input"
                  rows="2"
                />
                <textarea
                  placeholder="Feedback text..."
                  value={newFeedback.feedback}
                  onChange={(e) => setNewFeedback({...newFeedback, feedback: e.target.value})}
                  className="modal-input"
                  rows="3"
                />
                <textarea
                  placeholder="SQL query (optional)..."
                  value={newFeedback.sql_query}
                  onChange={(e) => setNewFeedback({...newFeedback, sql_query: e.target.value})}
                  className="modal-input"
                  rows="2"
                />
                <textarea
                  placeholder="Response (optional)..."
                  value={newFeedback.response}
                  onChange={(e) => setNewFeedback({...newFeedback, response: e.target.value})}
                  className="modal-input"
                  rows="2"
                />
              </div>
              <div className="modal-footer">
                <button 
                  onClick={() => setShowAddFeedbackModal(false)}
                  className="btn-cancel"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => {
                    createFeedback();
                    setShowAddFeedbackModal(false);
                  }}
                  disabled={loading || !newFeedback.original_query.trim() || !newFeedback.feedback.trim()}
                  className="btn-save"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};

export default AdminInterface;