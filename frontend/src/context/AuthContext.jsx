import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Helper to determine dashboard path based on role
  const getRoleDashboard = (role) => {
    switch (role) {
      case 'CUSTOMER':
        return '/customer/dashboard';
      case 'RESTAURANT_OWNER':
        return '/restaurant/dashboard';
      case 'DELIVERY_PARTNER':
        return '/delivery/dashboard';
      default:
        return '/';
    }
  };

  // Verify existing session on initial application mount
  useEffect(() => {
    let isMounted = true;

    async function checkAuthSession() {
      const storedToken = localStorage.getItem('campus_byte_token');
      // If no token stored, skip network check
      if (!storedToken) {
        if (isMounted) setLoading(false);
        return;
      }

      try {
        const profile = await authApi.getMe();
        if (isMounted) {
          setUser(profile);
          setError(null);
        }
      } catch (err) {
        // Session expired or token invalidated
        localStorage.removeItem('campus_byte_token');
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    checkAuthSession();

    return () => {
      isMounted = false;
    };
  }, []);

  // Login handler
  const login = async (email, password) => {
    setError(null);
    try {
      const data = await authApi.login({ email, password });
      localStorage.setItem('campus_byte_token', data.access_token);
      setUser(data.user);
      return data.user;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(msg);
      throw new Error(msg);
    }
  };

  // Registration handlers
  const registerCustomer = async (formData) => {
    setError(null);
    try {
      const newUser = await authApi.registerCustomer(formData);
      return newUser;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Customer registration failed.';
      setError(msg);
      throw new Error(msg);
    }
  };

  const registerRestaurantOwner = async (formData) => {
    setError(null);
    try {
      const newUser = await authApi.registerRestaurantOwner(formData);
      return newUser;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Restaurant owner registration failed.';
      setError(msg);
      throw new Error(msg);
    }
  };

  const registerDeliveryPartner = async (formData) => {
    setError(null);
    try {
      const newUser = await authApi.registerDeliveryPartner(formData);
      return newUser;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Delivery partner registration failed.';
      setError(msg);
      throw new Error(msg);
    }
  };

  // Logout handler
  const logout = async () => {
    try {
      await authApi.logout();
    } catch (err) {
      // Ignore network errors on logout, proceed with local session purge
    } finally {
      localStorage.removeItem('campus_byte_token');
      setUser(null);
      setError(null);
    }
  };

  const value = {
    user,
    role: user?.role || null,
    isAuthenticated: Boolean(user),
    loading,
    error,
    login,
    registerCustomer,
    registerRestaurantOwner,
    registerDeliveryPartner,
    logout,
    getRoleDashboard,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
