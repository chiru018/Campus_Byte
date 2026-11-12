import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import LandingPage from '../pages/public/LandingPage';
import LoginPage from '../pages/public/LoginPage';
import CustomerRegisterPage from '../pages/public/CustomerRegisterPage';
import RestaurantOwnerRegisterPage from '../pages/public/RestaurantOwnerRegisterPage';
import DeliveryPartnerRegisterPage from '../pages/public/DeliveryPartnerRegisterPage';
import UnauthorizedPage from '../pages/public/UnauthorizedPage';
import RestaurantListPage from '../pages/public/RestaurantListPage';
import RestaurantDetailPage from '../pages/public/RestaurantDetailPage';

import ProtectedRoute from './ProtectedRoute';
import CustomerDashboard from '../pages/customer/CustomerDashboard';
import CartPage from '../pages/customer/CartPage';
import CheckoutPage from '../pages/customer/CheckoutPage';
import OrderConfirmationPage from '../pages/customer/OrderConfirmationPage';
import MyOrdersPage from '../pages/customer/MyOrdersPage';
import OrderTrackingPage from '../pages/customer/OrderTrackingPage';

import RestaurantDashboard from '../pages/restaurant/RestaurantDashboard';
import RestaurantProfilePage from '../pages/restaurant/RestaurantProfilePage';
import RestaurantOrdersPage from '../pages/restaurant/RestaurantOrdersPage';
import RestaurantOrderDetailPage from '../pages/restaurant/RestaurantOrderDetailPage';
import MenuManagementPage from '../pages/restaurant/MenuManagementPage';
import AddMenuItemPage from '../pages/restaurant/AddMenuItemPage';
import EditMenuItemPage from '../pages/restaurant/EditMenuItemPage';
import DeliveryDashboard from '../pages/delivery/DeliveryDashboard';
import DeliveryAvailableOrdersPage from '../pages/delivery/DeliveryAvailableOrdersPage';
import DeliveryActivePage from '../pages/delivery/DeliveryActivePage';
import DeliveryHistoryPage from '../pages/delivery/DeliveryHistoryPage';
import DeliveryProfilePage from '../pages/delivery/DeliveryProfilePage';

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        {/* Public & Customer Discovery Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/restaurants" element={<RestaurantListPage />} />
        <Route path="/restaurants/:restaurantId" element={<RestaurantDetailPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register/customer" element={<CustomerRegisterPage />} />
        <Route path="/register/restaurant-owner" element={<RestaurantOwnerRegisterPage />} />
        <Route path="/register/delivery-partner" element={<DeliveryPartnerRegisterPage />} />
        <Route path="/delivery/register" element={<DeliveryPartnerRegisterPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* Customer Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={['CUSTOMER']} />}>
          <Route path="/customer/dashboard" element={<CustomerDashboard />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/order-confirmation/:orderId" element={<OrderConfirmationPage />} />
          <Route path="/my-orders" element={<MyOrdersPage />} />
          <Route path="/my-orders/:orderId" element={<OrderTrackingPage />} />
        </Route>

        {/* Restaurant Owner Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={['RESTAURANT_OWNER']} />}>
          <Route path="/restaurant/dashboard" element={<RestaurantDashboard />} />
          <Route path="/restaurant/orders" element={<RestaurantOrdersPage />} />
          <Route path="/restaurant/orders/:orderId" element={<RestaurantOrderDetailPage />} />
          <Route path="/restaurant/profile" element={<RestaurantProfilePage />} />
          <Route path="/restaurant/menu" element={<MenuManagementPage />} />
          <Route path="/restaurant/menu/add" element={<AddMenuItemPage />} />
          <Route path="/restaurant/menu/edit/:itemId" element={<EditMenuItemPage />} />
        </Route>

        {/* Delivery Partner Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={['DELIVERY_PARTNER']} />}>
          <Route path="/delivery/dashboard" element={<DeliveryDashboard />} />
          <Route path="/delivery/available-orders" element={<DeliveryAvailableOrdersPage />} />
          <Route path="/delivery/active-delivery" element={<DeliveryActivePage />} />
          <Route path="/delivery/history" element={<DeliveryHistoryPage />} />
          <Route path="/delivery/profile" element={<DeliveryProfilePage />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
