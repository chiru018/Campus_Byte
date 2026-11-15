import api from './api';

export const insightsService = {
  /**
   * Fetch customer spending summary & monthly trends.
   */
  async getSpendingSummary() {
    const response = await api.get('/api/insights/summary');
    return response.data;
  },

  /**
   * Fetch customer ordering patterns (top dishes, favourite restaurants, categories).
   */
  async getOrderingPatterns() {
    const response = await api.get('/api/insights/patterns');
    return response.data;
  },

  /**
   * Fetch personalized food recommendations.
   * @param {number} limit
   */
  async getRecommendations(limit = 6) {
    const response = await api.get('/api/insights/recommendations', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Fetch AI-generated dining narrative & key highlights (Gemini or resilient fallback).
   */
  async getAiSummary() {
    const response = await api.get('/api/insights/ai-summary');
    return response.data;
  },
};

export default insightsService;

