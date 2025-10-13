const config = {
  API_URL: process.env.REACT_APP_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`,
  MAIN_API_URL: process.env.REACT_APP_MAIN_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`,
  CCR_API_URL: process.env.REACT_APP_CCR_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`
};

export default config;