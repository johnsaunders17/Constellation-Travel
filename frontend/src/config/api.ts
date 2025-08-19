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

// Mock data for when backend is not available
export const MOCK_DATA = {
  deals: [
    {
      id: 1,
      type: 'flight',
      origin: 'EMA',
      destination: 'ALC',
      departureDate: '2024-09-15',
      returnDate: '2024-09-22',
      price: 189,
      airline: 'Ryanair',
      stops: 0,
      duration: '2h 45m',
      isDateValid: true,
      flight: {
        departure: '2024-09-15',
        arrival: '2024-09-22',
        carrier: 'Ryanair',
        isDateValid: true
      },
      hotel: {
        stars: 4,
        isDateValid: true
      }
    },
    {
      id: 2,
      type: 'hotel',
      name: 'Hotel Marina Delfin',
      location: 'Alicante',
      checkIn: '2024-09-15',
      checkOut: '2024-09-22',
      price: 420,
      stars: 4,
      board: 'RO',
      isDateValid: true,
      flight: {
        departure: '2024-09-15',
        arrival: '2024-09-22',
        carrier: 'Hotel',
        isDateValid: true
      },
      hotel: {
        stars: 4,
        isDateValid: true
      }
    },
    {
      id: 3,
      type: 'package',
      origin: 'EMA',
      destination: 'ALC',
      departureDate: '2024-09-15',
      returnDate: '2024-09-22',
      flightPrice: 189,
      hotelPrice: 420,
      totalPrice: 609,
      savings: 50,
      isDateValid: true,
      flight: {
        departure: '2024-09-15',
        arrival: '2024-09-22',
        carrier: 'Ryanair',
        isDateValid: true
      },
      hotel: {
        stars: 4,
        isDateValid: true
      }
    }
  ],
  flights: [
    {
      id: 'flight1',
      origin: 'EMA',
      destination: 'ALC',
      departureTime: '06:30',
      arrivalTime: '09:15',
      duration: '2h 45m',
      price: 189,
      airline: 'Ryanair',
      stops: 0,
      aircraft: 'Boeing 737'
    },
    {
      id: 'flight2',
      origin: 'EMA',
      destination: 'ALC',
      departureTime: '14:20',
      arrivalTime: '17:05',
      duration: '2h 45m',
      price: 245,
      airline: 'Jet2',
      stops: 0,
      aircraft: 'Airbus A321'
    }
  ],
  hotels: [
    {
      id: 'hotel1',
      name: 'Hotel Marina Delfin',
      location: 'Alicante',
      stars: 4,
      price: 60,
      board: 'RO',
      amenities: ['Pool', 'WiFi', 'Restaurant', 'Beach Access'],
      rating: 4.2,
      reviews: 1247
    },
    {
      id: 'hotel2',
      name: 'Hotel Alicante Golf',
      location: 'Alicante',
      stars: 3,
      price: 45,
      board: 'BB',
      amenities: ['Golf Course', 'WiFi', 'Restaurant'],
      rating: 3.8,
      reviews: 892
    }
  ]
};
