import api from './api';

export const restaurantService = {
  // Public listing with pagination, search, and availability filter
  getRestaurants: async ({ page = 1, size = 20, search = '', isOpen = null } = {}) => {
    const params = { page, size };
    if (search && search.trim()) {
      params.search = search.trim();
    }
    if (isOpen !== null && isOpen !== undefined && isOpen !== '') {
      params.is_open = isOpen;
    }
    const response = await api.get('/api/restaurants', { params });
    return response.data;
  },

  // Public get by ID
  getRestaurantById: async (restaurantId) => {
    const response = await api.get(`/api/restaurants/${restaurantId}`);
    return response.data;
  },

  // Authenticated Owner: get my restaurant
  getMyRestaurant: async () => {
    const response = await api.get('/api/restaurants/my-restaurant');
    return response.data;
  },

  // Authenticated Owner: create restaurant
  createRestaurant: async (restaurantData) => {
    const response = await api.post('/api/restaurants', restaurantData);
    return response.data;
  },

  // Authenticated Owner: update profile
  updateRestaurant: async (restaurantId, updateData) => {
    const response = await api.put(`/api/restaurants/${restaurantId}`, updateData);
    return response.data;
  },

  // Authenticated Owner: toggle/set open status
  updateRestaurantAvailability: async (restaurantId, isOpen) => {
    const response = await api.patch(`/api/restaurants/${restaurantId}/availability`, {
      is_open: isOpen,
    });
    return response.data;
  },

  // Authenticated Owner: get stats (total menu items, profile completion, etc.)
  getRestaurantStats: async (restaurantId) => {
    const response = await api.get(`/api/restaurants/${restaurantId}/stats`);
    return response.data;
  },

  // Authenticated Owner: delete/deactivate restaurant
  deleteRestaurant: async (restaurantId) => {
    const response = await api.delete(`/api/restaurants/${restaurantId}`);
    return response.data;
  },
};

export default restaurantService;

