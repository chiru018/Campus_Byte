import api from './api';

export const reviewService = {
  /**
   * Submit a new customer review for a delivered order.
   * @param {Object} data - { order_id, restaurant_id, rating, comment }
   */
  async submitReview(data) {
    const response = await api.post('/api/reviews', data);
    return response.data;
  },

  /**
   * Fetch current authenticated customer's submitted reviews.
   */
  async getMyReviews() {
    const response = await api.get('/api/reviews/my-reviews');
    return response.data;
  },

  /**
   * Update an existing review by ID.
   * @param {string} reviewId
   * @param {Object} data - { rating, comment }
   */
  async updateReview(reviewId, data) {
    const response = await api.put(`/api/reviews/${reviewId}`, data);
    return response.data;
  },

  /**
   * Delete an existing review by ID.
   * @param {string} reviewId
   */
  async deleteReview(reviewId) {
    const response = await api.delete(`/api/reviews/${reviewId}`);
    return response.data;
  },

  /**
   * Fetch public restaurant review summary and feedback list.
   * @param {string} restaurantId
   */
  async getRestaurantReviews(restaurantId) {
    const response = await api.get(`/api/reviews/restaurant/${restaurantId}`);
    return response.data;
  },
};

export default reviewService;

