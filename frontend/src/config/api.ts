// API Configuration for different environments
export const API_CONFIG = {
  // Development (localhost)
  development: {
    baseUrl: 'http://localhost:5001',
    timeout: 10000
  },
  // Production (GitHub Pages)
  production: {
    baseUrl: 'https://constellation-travel-backend.onrender.com',
    timeout: 15000
  }
};

// Get current environment
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const isProduction = window.location.hostname.includes('github.io');

// Select appropriate config
export const getApiConfig = () => {
  if (isDevelopment) {
    return API_CONFIG.development;
  } else if (isProduction) {
    return API_CONFIG.production;
  }
  // Default to development
  return API_CONFIG.development;
};

// API endpoints
export const API_ENDPOINTS = {
  deals: '/api/deals',
  search: '/api/search',
  flightsSearch: '/api/flights/search',
  hotelsSearch: '/api/hotels/search'
};

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string) => {
  const config = getApiConfig();
  return `${config.baseUrl}${endpoint}`;
};
