import api from './api';

export const menuService = {
  // Public: get standard categories list
  getCategories: async () => {
    const response = await api.get('/api/menu/categories');
    return response.data;
  },

  // Public / Owner: list menu items for restaurant with category, availability, and search filter
  getRestaurantMenu: async (restaurantId, { category = '', isAvailable = null, search = '' } = {}) => {
    const params = {};
    if (category && category.trim()) {
      params.category = category.trim();
    }
    if (isAvailable !== null && isAvailable !== undefined && isAvailable !== '') {
      params.is_available = isAvailable;
    }
    if (search && search.trim()) {
      params.search = search.trim();
    }
    const response = await api.get(`/api/restaurants/${restaurantId}/menu`, { params });
    return response.data;
  },

  // Public: get individual menu item details
  getMenuItem: async (itemId) => {
    const response = await api.get(`/api/menu/${itemId}`);
    return response.data;
  },

  // Authenticated Owner: add menu item
  createMenuItem: async (restaurantId, itemData) => {
    const response = await api.post(`/api/restaurants/${restaurantId}/menu`, itemData);
    return response.data;
  },

  // Authenticated Owner: update menu item
  updateMenuItem: async (itemId, updateData) => {
    const response = await api.put(`/api/menu/${itemId}`, updateData);
    return response.data;
  },

  // Authenticated Owner: toggle item availability
  updateMenuItemAvailability: async (itemId, isAvailable) => {
    const response = await api.patch(`/api/menu/${itemId}/availability`, {
      is_available: isAvailable,
    });
    return response.data;
  },

  // Authenticated Owner: delete/deactivate item
  deleteMenuItem: async (itemId) => {
    const response = await api.delete(`/api/menu/${itemId}`);
    return response.data;
  },
};

export default menuService;

