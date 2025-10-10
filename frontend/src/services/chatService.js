import axios from 'axios';
import config from '../config/api';

const API_BASE_URL = config.MAIN_API_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  async sendMessage(message, sessionId = null) {
    try {
      const response = await api.post('/chat', {
        message,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  },

  async getSessionHistory(sessionId) {
    try {
      const response = await api.get(`/sessions/${sessionId}/history`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get session history');
    }
  },

  async refreshSchema() {
    try {
      const response = await api.post('/schema/refresh');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to refresh schema');
    }
  },

  async confirmQuestion(confirmed, sessionId) {
    try {
      const response = await api.post('/confirm', {
        confirmed: confirmed,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to confirm question');
    }
  },

  async refineMessage(originalQuestion, feedback, sessionId) {
    try {
      const response = await api.post('/refine', {
        original_question: originalQuestion,
        feedback: feedback,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to refine message');
    }
  },

  async generateReport(question, sqlQuery, rawData, sessionId) {
    try {
      const response = await api.post('/generate-report', {
        question: question,
        sql_query: sqlQuery,
        raw_data: rawData,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to generate report');
    }
  },

  async submitFeedback(feedbackData) {
    try {
      const response = await api.post('/feedback', feedbackData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to submit feedback');
    }
  },

  async getPendingFeedbacks() {
    try {
      const response = await api.get('/admin/feedbacks');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get feedbacks');
    }
  },

  async approveFeedback(feedbackId) {
    try {
      const response = await api.post(`/admin/feedbacks/${feedbackId}/approve`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to approve feedback');
    }
  },

  async rejectFeedback(feedbackId) {
    try {
      const response = await api.post(`/admin/feedbacks/${feedbackId}/reject`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to reject feedback');
    }
  },

  async getTrainingData() {
    try {
      const response = await api.get('/admin/training-data');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get training data');
    }
  },

  async addTrainingData(trainingData) {
    try {
      const response = await api.post('/admin/training-data', trainingData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to add training data');
    }
  },

  async processWithFeedback(originalQuery, feedback, sessionId) {
    try {
      const response = await api.post('/process-feedback', {
        original_query: originalQuery,
        feedback: feedback,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to process feedback');
    }
  },

  async healthCheck() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Backend service unavailable');
    }
  },

  async adminLogin(username, password) {
    try {
      const response = await api.post('/admin/login', {
        username: username,
        password: password
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  },

  async getAllFeedbacks() {
    try {
      const response = await api.get('/admin/feedbacks/all');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get all feedbacks');
    }
  },

  async createFeedback(feedbackData) {
    try {
      const response = await api.post('/admin/feedbacks', feedbackData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create feedback');
    }
  },

  async updateFeedback(feedbackId, updateData) {
    try {
      const response = await api.put(`/admin/feedbacks/${feedbackId}`, updateData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update feedback');
    }
  },

  async deleteFeedback(feedbackId) {
    try {
      const response = await api.delete(`/admin/feedbacks/${feedbackId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete feedback');
    }
  }
};