// API Configuration
const config = {
  // Main backend API
  MAIN_API_URL: process.env.REACT_APP_MAIN_API_URL || 'http://localhost:8000',
  
  // CCR backend API (now unified with main API)
  CCR_API_URL: process.env.REACT_APP_CCR_API_URL || 'http://localhost:8000',
};

export default config;