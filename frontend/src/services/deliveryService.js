import api from './api';

export const deliveryService = {
  // Profile & Availability
  getProfile: async () => {
    const response = await api.get('/api/delivery/profile');
    return response.data;
  },

  updateProfile: async (data) => {
    const response = await api.patch('/api/delivery/profile', data);
    return response.data;
  },

  updateAvailability: async (availability_status) => {
    const response = await api.patch('/api/delivery/availability', { availability_status });
    return response.data;
  },

  // Dashboard & Statistics
  getDashboardStatistics: async () => {
    const response = await api.get('/api/delivery/dashboard/statistics');
    return response.data;
  },

  // Available Orders
  getAvailableOrders: async (page = 1, size = 20) => {
    const response = await api.get('/api/delivery/available-orders', {
      params: { page, size },
    });
    return response.data;
  },

  acceptOrder: async (orderId) => {
    const response = await api.post(`/api/delivery/assignments/${orderId}/accept`);
    return response.data;
  },

  // Active Delivery
  getActiveDelivery: async () => {
    const response = await api.get('/api/delivery/active-delivery');
    return response.data;
  },

  getAssignmentDetail: async (orderId) => {
    const response = await api.get(`/api/delivery/assignments/${orderId}`);
    return response.data;
  },

  // Delivery Transitions
  confirmPickup: async (orderId) => {
    const response = await api.patch(`/api/delivery/assignments/${orderId}/pickup`);
    return response.data;
  },

  startDelivery: async (orderId) => {
    const response = await api.patch(`/api/delivery/assignments/${orderId}/start-delivery`);
    return response.data;
  },

  confirmCOD: async (orderId, collectedAmount) => {
    const response = await api.post(`/api/delivery/assignments/${orderId}/confirm-cod`, {
      confirm_cash_collected: true,
      collected_amount: collectedAmount,
    });
    return response.data;
  },

  getCODStatus: async (orderId) => {
    const response = await api.get(`/api/delivery/assignments/${orderId}/cod-status`);
    return response.data;
  },

  completeDelivery: async (orderId, options = {}) => {
    const payload = {
      confirm_delivered: options.confirm_delivered ?? true,
      confirm_cash_collected: options.confirm_cash_collected,
      collected_amount: options.collected_amount,
    };
    const response = await api.patch(`/api/delivery/assignments/${orderId}/complete`, payload);
    return response.data;
  },

  // History & Audit
  getDeliveryHistory: async (params = {}) => {
    const response = await api.get('/api/delivery/history', { params });
    return response.data;
  },

  getOrderHistory: async (orderId) => {
    const response = await api.get(`/api/delivery/assignments/${orderId}/history`);
    return response.data;
  },
};

export default deliveryService;

