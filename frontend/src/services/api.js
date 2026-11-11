import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  withCredentials: true, // Sends secure HttpOnly cookies across origins
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request interceptor: attaches Bearer token if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('campus_byte_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: catches 401 unauthenticated
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear client state on authentication expiration
      localStorage.removeItem('campus_byte_token');
    }
    return Promise.reject(error);
  }
);

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getApiRoot = async () => {
  const response = await api.get('/');
  return response.data;
};

// ==========================================
// Authentication APIs (Phase 3)
// ==========================================
export const authApi = {
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },
  registerCustomer: async (data) => {
    const response = await api.post('/api/auth/register/customer', data);
    return response.data;
  },
  registerRestaurantOwner: async (data) => {
    const response = await api.post('/api/auth/register/restaurant-owner', data);
    return response.data;
  },
  registerDeliveryPartner: async (data) => {
    const response = await api.post('/api/auth/register/delivery-partner', data);
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  logout: async () => {
    const response = await api.post('/api/auth/logout');
    return response.data;
  },
};

export default api;
