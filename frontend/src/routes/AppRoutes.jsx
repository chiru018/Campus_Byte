import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import LandingPage from '../pages/public/LandingPage';
import LoginPage from '../pages/public/LoginPage';
import CustomerRegisterPage from '../pages/public/CustomerRegisterPage';
import RestaurantOwnerRegisterPage from '../pages/public/RestaurantOwnerRegisterPage';
import DeliveryPartnerRegisterPage from '../pages/public/DeliveryPartnerRegisterPage';
import UnauthorizedPage from '../pages/public/UnauthorizedPage';

import ProtectedRoute from './ProtectedRoute';
import CustomerDashboard from '../pages/customer/CustomerDashboard';
import RestaurantDashboard from '../pages/restaurant/RestaurantDashboard';
import DeliveryDashboard from '../pages/delivery/DeliveryDashboard';

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register/customer" element={<CustomerRegisterPage />} />
        <Route path="/register/restaurant-owner" element={<RestaurantOwnerRegisterPage />} />
        <Route path="/register/delivery-partner" element={<DeliveryPartnerRegisterPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* Customer Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={['CUSTOMER']} />}>
          <Route path="/customer/dashboard" element={<CustomerDashboard />} />
        </Route>

        {/* Restaurant Owner Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={['RESTAURANT_OWNER']} />}>
          <Route path="/restaurant/dashboard" element={<RestaurantDashboard />} />
        </Route>

        {/* Delivery Partner Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={['DELIVERY_PARTNER']} />}>
          <Route path="/delivery/dashboard" element={<DeliveryDashboard />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
