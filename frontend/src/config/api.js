// Dynamic API URL configuration that adapts to any domain/port
const getApiUrl = () => {
  // If environment variable is set, use it
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const port = window.location.port;
  
  // For localhost development, use port 8000
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:8000`;
  }
  
  // For production domains, try same port first (proxy setup)
  return `${protocol}//${hostname}:${port}`;
};

// Fallback API URLs to try if primary fails
const getApiFallbacks = () => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  
  return [
    `${protocol}//${hostname}:8000`,  // Direct backend
    `http://${hostname}:8000`,       // HTTP backend
    `${protocol}//${hostname}:3000`,  // Same as frontend
  ];
};

// Enhanced fetch with automatic fallback
const apiRequest = async (endpoint, options = {}) => {
  const primaryUrl = getApiUrl();
  const fallbacks = getApiFallbacks();
  const allUrls = [primaryUrl, ...fallbacks.filter(url => url !== primaryUrl)];
  
  for (const baseUrl of allUrls) {
    try {
      const response = await fetch(`${baseUrl}${endpoint}`, options);
      if (response.ok) {
        return response;
      }
    } catch (error) {
      console.warn(`API request failed for ${baseUrl}${endpoint}:`, error.message);
    }
  }
  
  throw new Error(`All API endpoints failed for ${endpoint}`);
};

const config = {
  API_URL: getApiUrl(),
  MAIN_API_URL: getApiUrl(),
  CCR_API_URL: getApiUrl(),
  // Enhanced request method
  request: apiRequest
};

export default config;