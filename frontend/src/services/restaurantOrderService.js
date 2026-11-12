import api from './api';

export const restaurantOrderService = {
  /**
   * Retrieve paginated orders for the authenticated owner's restaurant.
   */
  getOrders: async ({ page = 1, size = 20, status = null, search = '' } = {}) => {
    const params = { page, size };
    if (status && status !== 'ALL') {
      params.status = status;
    }
    if (search && search.trim()) {
      params.search = search.trim();
    }
    const response = await api.get('/api/restaurant/orders', { params });
    return response.data;
  },

  /**
   * Retrieve aggregate order statistics across all lifecycle states.
   */
  getOrderStats: async () => {
    const response = await api.get('/api/restaurant/orders/statistics');
    return response.data;
  },

  /**
   * Poll for newly placed pending orders since cursor.
   */
  getNotifications: async (since = null) => {
    const params = {};
    if (since) {
      params.since = since;
    }
    const response = await api.get('/api/restaurant/orders/notifications', { params });
    return response.data;
  },

  /**
   * Retrieve single order details strictly for owner's restaurant.
   */
  getOrderById: async (orderId) => {
    const response = await api.get(`/api/restaurant/orders/${orderId}`);
    return response.data;
  },

  /**
   * Retrieve chronological status transition audit history.
   */
  getOrderHistory: async (orderId) => {
    const response = await api.get(`/api/restaurant/orders/${orderId}/history`);
    return response.data;
  },

  /**
   * Accept an incoming PENDING order.
   */
  acceptOrder: async (orderId) => {
    const response = await api.patch(`/api/restaurant/orders/${orderId}/accept`);
    return response.data;
  },

  /**
   * Reject a PENDING order with mandatory reason.
   */
  rejectOrder: async (orderId, reason) => {
    const response = await api.patch(`/api/restaurant/orders/${orderId}/reject`, { reason });
    return response.data;
  },

  /**
   * Transition order from ACCEPTED to PREPARING.
   */
  startPreparation: async (orderId) => {
    const response = await api.patch(`/api/restaurant/orders/${orderId}/start-preparation`);
    return response.data;
  },

  /**
   * Transition order from PREPARING to READY_FOR_PICKUP.
   */
  markReadyForPickup: async (orderId) => {
    const response = await api.patch(`/api/restaurant/orders/${orderId}/ready-for-pickup`);
    return response.data;
  },
};

export default restaurantOrderService;
