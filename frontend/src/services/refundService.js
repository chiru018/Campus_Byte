import api from './api';

export const refundService = {
  /**
   * Submit a new customer refund request for a delivered order.
   * @param {Object} data - { order_id, issue_category, description, requested_amount }
   */
  async createRefundRequest(data) {
    const response = await api.post('/api/refunds', data);
    return response.data;
  },

  /**
   * Fetch current authenticated customer's refund requests.
   * @param {number} page
   * @param {number} size
   */
  async getMyRefundRequests(page = 1, size = 20) {
    const response = await api.get('/api/refunds/my-requests', {
      params: { page, size },
    });
    return response.data;
  },

  /**
   * Fetch details of a specific customer refund request.
   * @param {string} refundId
   */
  async getCustomerRefundDetail(refundId) {
    const response = await api.get(`/api/refunds/${refundId}`);
    return response.data;
  },

  /**
   * (Restaurant Owner) Fetch refund requests submitted for owner's restaurant.
   * @param {Object} params - { status, page, size }
   */
  async getRestaurantRefunds(params = {}) {
    const response = await api.get('/api/restaurant/refunds', { params });
    return response.data;
  },

  /**
   * (Restaurant Owner) Fetch details of a specific refund request.
   * @param {string} refundId
   */
  async getRestaurantRefundDetail(refundId) {
    const response = await api.get(`/api/restaurant/refunds/${refundId}`);
    return response.data;
  },

  /**
   * (Restaurant Owner) Move refund status to UNDER_REVIEW.
   * @param {string} refundId
   */
  async markUnderReview(refundId) {
    const response = await api.patch(`/api/restaurant/refunds/${refundId}/under-review`);
    return response.data;
  },

  /**
   * (Restaurant Owner) Approve refund request with approved amount.
   * @param {string} refundId
   * @param {Object} data - { approved_amount, resolution_notes }
   */
  async approveRefund(refundId, data) {
    const response = await api.patch(`/api/restaurant/refunds/${refundId}/approve`, data);
    return response.data;
  },

  /**
   * (Restaurant Owner) Reject refund request with mandatory explanation.
   * @param {string} refundId
   * @param {Object} data - { explanation }
   */
  async rejectRefund(refundId, data) {
    const response = await api.patch(`/api/restaurant/refunds/${refundId}/reject`, data);
    return response.data;
  },

  /**
   * (Restaurant Owner) Mark approved refund as resolved.
   * @param {string} refundId
   * @param {Object} data - { resolution_notes }
   */
  async resolveRefund(refundId, data = {}) {
    const response = await api.patch(`/api/restaurant/refunds/${refundId}/resolve`, data);
    return response.data;
  },
};

export default refundService;

