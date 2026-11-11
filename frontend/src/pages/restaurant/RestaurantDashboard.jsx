import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Store,
  UtensilsCrossed,
  CheckCircle,
  XCircle,
  PlusCircle,
  ArrowRight,
  Info,
  Clock,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import restaurantService from '../../services/restaurantService';
import RestaurantSidebar from '../../components/navigation/RestaurantSidebar';
import Button from '../../components/common/Button';
import './Restaurant.scss';

export default function RestaurantDashboard() {
  const { user } = useAuth();
  const [restaurant, setRestaurant] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [togglingStatus, setTogglingStatus] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const myRest = await restaurantService.getMyRestaurant();
      setRestaurant(myRest);
      if (myRest?.id) {
        const statsData = await restaurantService.getRestaurantStats(myRest.id);
        setStats(statsData);
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setRestaurant(null);
      } else {
        setError(err.response?.data?.detail || 'Failed to load restaurant dashboard.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleToggleAvailability = async () => {
    if (!restaurant) return;
    setTogglingStatus(true);
    try {
      const newStatus = !restaurant.is_open;
      const updated = await restaurantService.updateRestaurantAvailability(
        restaurant.id,
        newStatus
      );
      setRestaurant(updated);
      if (stats) {
        setStats({ ...stats, is_open: newStatus });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update availability.');
    } finally {
      setTogglingStatus(false);
    }
  };

  if (loading) {
    return (
      <div className="restaurant-layout">
        <div style={{ padding: '3rem', textAlign: 'center', width: '100%' }}>
          <p>Loading restaurant dashboard...</p>
        </div>
      </div>
    );
  }

  // If owner hasn't created a restaurant yet
  if (!restaurant) {
    return (
      <div className="restaurant-layout">
        <div className="restaurant-content" style={{ margin: '0 auto' }}>
          <div className="empty-state">
            <Store size={48} />
            <h3>No Restaurant Registered</h3>
            <p>
              Welcome, {user?.full_name}! To start serving campus diners, please set up your restaurant profile.
            </p>
            <Link to="/restaurant/profile">
              <Button variant="primary" icon={PlusCircle}>
                Register Your Restaurant
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="restaurant-layout">
      <RestaurantSidebar
        restaurantName={restaurant.name}
        isOpen={restaurant.is_open}
      />

      <main className="restaurant-content">
        <div className="restaurant-content__header">
          <div>
            <h1>{restaurant.name}</h1>
            <p>{restaurant.address} • Contact: {restaurant.contact_number}</p>
          </div>

          <div className="header-actions">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={restaurant.is_open}
                onChange={handleToggleAvailability}
                disabled={togglingStatus}
              />
              <span className="switch-slider"></span>
              <span className="toggle-label">
                {restaurant.is_open ? 'Accepting Orders' : 'Outlet Closed'}
              </span>
            </label>
            <Link to="/restaurant/menu/add">
              <Button variant="primary" size="sm" icon={PlusCircle}>
                Add Food Item
              </Button>
            </Link>
          </div>
        </div>

        {error && (
          <div style={{ padding: '1rem', backgroundColor: '#FEE2E2', color: '#B91C1C', borderRadius: '0.75rem', marginBottom: '1.5rem' }}>
            {error}
          </div>
        )}

        {/* Informational Banner */}
        <div className="info-banner">
          <Info size={24} className="banner-icon" />
          <div>
            <h4>Module Notice: Real-Time Kitchen Orders</h4>
            <p>
              Phase 4 handles full menu, pricing, and availability management. Customer checkout, kitchen dispatch queues, and student delivery courier dispatch will become active in Phase 5.
            </p>
          </div>
        </div>

        {/* Real KPI Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-card__icon primary">
              <UtensilsCrossed size={22} />
            </div>
            <div className="stat-card__value">{stats?.total_menu_items ?? 0}</div>
            <div className="stat-card__label">Total Menu Items</div>
          </div>

          <div className="stat-card">
            <div className="stat-card__icon success">
              <CheckCircle size={22} />
            </div>
            <div className="stat-card__value">{stats?.available_menu_items ?? 0}</div>
            <div className="stat-card__label">Items In Stock</div>
          </div>

          <div className="stat-card">
            <div className="stat-card__icon warning">
              <XCircle size={22} />
            </div>
            <div className="stat-card__value">{stats?.unavailable_menu_items ?? 0}</div>
            <div className="stat-card__label">Items Out of Stock</div>
          </div>

          <div className="stat-card">
            <div className="stat-card__icon info">
              <Sparkles size={22} />
            </div>
            <div className="stat-card__value">{stats?.profile_completion_percentage ?? 80}%</div>
            <div className="stat-card__label">Profile Completion</div>
            <div className="progress-container">
              <div
                className="progress-bar"
                style={{ width: `${stats?.profile_completion_percentage ?? 80}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Quick Links Card */}
        <div className="form-card">
          <h3 className="form-card__title">Quick Management Actions</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
            <Link
              to="/restaurant/menu"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1.25rem',
                border: '1px solid #E5E7EB',
                borderRadius: '0.75rem',
                textDecoration: 'none',
                color: '#111827',
              }}
            >
              <div>
                <strong>Manage Menu Catalog</strong>
                <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8rem', color: '#6B7280' }}>
                  Update prices, food stock, & categories
                </p>
              </div>
              <ArrowRight size={18} color="#F97316" />
            </Link>

            <Link
              to="/restaurant/profile"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1.25rem',
                border: '1px solid #E5E7EB',
                borderRadius: '0.75rem',
                textDecoration: 'none',
                color: '#111827',
              }}
            >
              <div>
                <strong>Edit Restaurant Profile</strong>
                <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8rem', color: '#6B7280' }}>
                  Address, contact number, & outlet branding
                </p>
              </div>
              <ArrowRight size={18} color="#F97316" />
            </Link>

            <Link
              to={`/restaurants/${restaurant.id}`}
              target="_blank"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1.25rem',
                border: '1px solid #E5E7EB',
                borderRadius: '0.75rem',
                textDecoration: 'none',
                color: '#111827',
              }}
            >
              <div>
                <strong>Customer View Preview</strong>
                <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8rem', color: '#6B7280' }}>
                  See how campus diners view your menu
                </p>
              </div>
              <ArrowRight size={18} color="#F97316" />
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
