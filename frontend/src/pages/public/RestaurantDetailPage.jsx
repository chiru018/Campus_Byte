import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Store,
  MapPin,
  Phone,
  ArrowLeft,
  UtensilsCrossed,
  Info,
  Clock,
} from 'lucide-react';
import restaurantService from '../../services/restaurantService';
import menuService from '../../services/menuService';
import Button from '../../components/common/Button';
import './Restaurants.scss';

export default function RestaurantDetailPage() {
  const { restaurantId } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setErrorMsg('');
      try {
        const restData = await restaurantService.getRestaurantById(restaurantId);
        setRestaurant(restData);

        const catData = await menuService.getCategories();
        setCategories(catData);

        const menuData = await menuService.getRestaurantMenu(restaurantId, {
          isAvailable: true, // Only show in-stock items to public diners
          category: selectedCategory,
        });
        setMenuItems(menuData.items || []);
      } catch (err) {
        setErrorMsg(err.response?.data?.detail || 'Failed to load restaurant details.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [restaurantId, selectedCategory]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '6rem 0', minHeight: '60vh' }}>
        <p>Loading restaurant menu...</p>
      </div>
    );
  }

  if (errorMsg || !restaurant) {
    return (
      <div className="container" style={{ padding: '4rem 1rem', textAlign: 'center' }}>
        <h2>Restaurant Not Found</h2>
        <p style={{ color: '#6B7280', marginBottom: '2rem' }}>
          {errorMsg || 'The requested food outlet is not available.'}
        </p>
        <Link to="/restaurants">
          <Button variant="primary" icon={ArrowLeft}>
            Browse Other Outlets
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="restaurant-detail-page">
      {/* Hero Banner */}
      <div
        className="hero-banner"
        style={{
          backgroundImage: restaurant.image_url ? `url(${restaurant.image_url})` : 'none',
        }}
      >
        <div className="container hero-content">
          <Link to="/restaurants" className="back-link">
            <ArrowLeft size={16} /> All Campus Restaurants
          </Link>

          <h1>{restaurant.name}</h1>
          <p className="description">
            {restaurant.description || 'Serving fresh daily meals to campus students and faculty.'}
          </p>

          <div className="meta-badges">
            <span className="badge-pill">
              <MapPin size={14} /> {restaurant.address}
            </span>
            {restaurant.contact_number && (
              <span className="badge-pill">
                <Phone size={14} /> {restaurant.contact_number}
              </span>
            )}
            <span
              className="badge-pill"
              style={{
                backgroundColor: restaurant.is_open ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
                color: restaurant.is_open ? '#A7F3D0' : '#FECACA',
              }}
            >
              <Clock size={14} /> {restaurant.is_open ? 'Open For Orders' : 'Currently Closed'}
            </span>
          </div>
        </div>
      </div>

      <div className="container">
        {/* Module Notice */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            backgroundColor: '#EFF6FF',
            border: '1px solid #BFDBFE',
            padding: '1rem',
            borderRadius: '0.75rem',
            color: '#1E40AF',
            marginBottom: '2rem',
            fontSize: '0.9rem',
          }}
        >
          <Info size={20} style={{ flexShrink: 0 }} />
          <span>
            <strong>Phase 4 Preview:</strong> Menu catalog, pricing, and food categories are live. Online cart ordering and door delivery checkout will launch in Phase 5.
          </span>
        </div>

        {/* Category Tabs */}
        <div className="category-tabs">
          <button
            type="button"
            className={selectedCategory === '' ? 'active' : ''}
            onClick={() => setSelectedCategory('')}
          >
            All Menu Items
          </button>
          {categories.map((c) => (
            <button
              key={c.key}
              type="button"
              className={selectedCategory === c.key ? 'active' : ''}
              onClick={() => setSelectedCategory(c.key)}
            >
              {c.label}
            </button>
          ))}
        </div>

        {/* Dishes Grid */}
        {menuItems.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '4rem 1rem', background: '#FFFFFF', borderRadius: '1rem', border: '1px dashed #E5E7EB' }}>
            <UtensilsCrossed size={40} color="#9CA3AF" style={{ marginBottom: '1rem' }} />
            <h3>No Available Items</h3>
            <p style={{ color: '#6B7280', maxWidth: '400px', margin: '0 auto' }}>
              No dishes are currently listed in this category for {restaurant.name}. Check back shortly!
            </p>
          </div>
        ) : (
          <div className="public-menu-grid">
            {menuItems.map((dish) => (
              <div key={dish.id} className="dish-card">
                <div className="dish-card__image">
                  {dish.image_url ? (
                    <img
                      src={dish.image_url}
                      alt={dish.name}
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  ) : (
                    <div className="dish-placeholder">
                      <UtensilsCrossed size={36} />
                    </div>
                  )}
                  <span className="category-tag">{dish.category}</span>
                </div>

                <div className="dish-card__details">
                  <h3>{dish.name}</h3>
                  <p>{dish.description || 'Prepared fresh upon order with quality ingredients.'}</p>

                  <div className="price-footer">
                    <span className="price">${parseFloat(dish.price).toFixed(2)}</span>
                    <span className="order-soon-pill">Orders in Phase 5</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
