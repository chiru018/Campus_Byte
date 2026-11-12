import api from './api';

export const orderService = {
  /**
   * Place a new food delivery order.
   * Calculates prices on backend and protects against double submit via idempotency key.
   */
  createOrder: async (orderData) => {
    const response = await api.post('/api/orders', orderData);
    return response.data;
  },

  /**
   * Retrieve customer's paginated order history with optional status filter.
   */
  getMyOrders: async ({ page = 1, size = 20, status = null } = {}) => {
    const params = { page, size };
    if (status) {
      params.status = status;
    }
    const response = await api.get('/api/orders/my-orders', { params });
    return response.data;
  },

  /**
   * Retrieve order detail and status history by ID. Enforces customer authorization.
   */
  getOrderById: async (orderId) => {
    const response = await api.get(`/api/orders/${orderId}`);
    return response.data;
  },

  /**
   * Cancel an order while in PENDING status.
   */
  cancelOrder: async (orderId, reason = null) => {
    const payload = reason ? { reason } : {};
    const response = await api.patch(`/api/orders/${orderId}/cancel`, payload);
    return response.data;
  },
};

export default orderService;

