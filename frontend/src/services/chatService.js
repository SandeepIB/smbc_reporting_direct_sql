import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

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

  async healthCheck() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Backend service unavailable');
    }
  }
};