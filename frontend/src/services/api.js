import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request interceptor for attaching future authorization tokens
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for consistent error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Phase 1 error handling
    console.error('API Error:', error.response?.data || error.message);
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

export default api;
