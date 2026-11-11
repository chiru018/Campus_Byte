import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Store,
  MapPin,
  Phone,
  ArrowLeft,
  UtensilsCrossed,
  Clock,
  ShoppingCart,
  Plus,
  Minus,
  AlertTriangle,
} from 'lucide-react';
import restaurantService from '../../services/restaurantService';
import menuService from '../../services/menuService';
import { useCart } from '../../context/CartContext';
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

  const {
    restaurant: cartRestaurant,
    items: cartItems,
    totalItems,
    totalAmount,
    addToCart,
    updateQuantity,
    getItemQuantity,
    conflictModal,
    confirmRestaurantSwitch,
    cancelRestaurantSwitch,
  } = useCart();

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

  const isCurrentCartRestaurant = cartRestaurant && cartRestaurant.id === restaurant.id;

  return (
    <div className="restaurant-detail-page" style={{ paddingBottom: isCurrentCartRestaurant && totalItems > 0 ? '5rem' : '2rem' }}>
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
              <Clock size={14} /> {restaurant.is_open ? 'Open For Delivery' : 'Currently Closed'}
            </span>
          </div>
        </div>
      </div>

      <div className="container">
        {!restaurant.is_open && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              backgroundColor: '#FEF2F2',
              border: '1px solid #FECACA',
              padding: '1rem',
              borderRadius: '0.75rem',
              color: '#991B1B',
              marginBottom: '2rem',
              fontSize: '0.95rem',
            }}
          >
            <AlertTriangle size={20} style={{ flexShrink: 0 }} />
            <span>
              <strong>Outlet Currently Closed:</strong> {restaurant.name} is not accepting orders at this time. You can still browse the menu catalog.
            </span>
          </div>
        )}

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
            {menuItems.map((dish) => {
              const qtyInCart = getItemQuantity(dish.id);
              return (
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

                      {!restaurant.is_open ? (
                        <span style={{ fontSize: '0.85rem', color: '#9CA3AF', fontWeight: '500' }}>Closed</span>
                      ) : qtyInCart > 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#FEF3C7', padding: '0.25rem 0.5rem', borderRadius: '0.5rem' }}>
                          <button
                            type="button"
                            onClick={() => updateQuantity(dish.id, qtyInCart - 1)}
                            style={{ background: '#FFFFFF', border: '1px solid #D1D5DB', borderRadius: '4px', width: '26px', height: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
                          >
                            <Minus size={14} color="#374151" />
                          </button>
                          <span style={{ fontWeight: '700', minWidth: '1.25rem', textAlign: 'center', color: '#B45309' }}>
                            {qtyInCart}
                          </span>
                          <button
                            type="button"
                            onClick={() => updateQuantity(dish.id, qtyInCart + 1)}
                            style={{ background: '#F59E0B', border: 'none', borderRadius: '4px', width: '26px', height: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#FFF' }}
                          >
                            <Plus size={14} />
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => addToCart(dish, restaurant)}
                          style={{
                            background: '#F59E0B',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '0.5rem',
                            padding: '0.45rem 0.9rem',
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.35rem',
                            cursor: 'pointer',
                            boxShadow: '0 2px 4px rgba(245, 158, 11, 0.25)',
                          }}
                        >
                          <Plus size={15} /> Add
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Floating Bottom Cart Bar (if current restaurant has items in cart) */}
      {isCurrentCartRestaurant && totalItems > 0 && (
        <div
          style={{
            position: 'fixed',
            bottom: '1.25rem',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 'calc(100% - 2rem)',
            maxWidth: '720px',
            backgroundColor: '#1E293B',
            color: '#FFFFFF',
            borderRadius: '1rem',
            padding: '0.875rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.4)',
            zIndex: 900,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div style={{ background: '#F59E0B', borderRadius: '50%', width: '38px', height: '38px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShoppingCart size={20} color="#FFFFFF" />
            </div>
            <div>
              <div style={{ fontWeight: '600', fontSize: '0.95rem' }}>
                {totalItems} {totalItems === 1 ? 'item' : 'items'} in your cart
              </div>
              <div style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
                Total: <strong style={{ color: '#FCD34D' }}>${totalAmount.toFixed(2)}</strong> (incl. $2.00 delivery)
              </div>
            </div>
          </div>
          <Link to="/cart">
            <Button variant="primary" size="small">
              View Cart & Checkout
            </Button>
          </Link>
        </div>
      )}

      {/* Cross-Restaurant Conflict Modal */}
      {conflictModal.isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '1rem',
              maxWidth: '460px',
              width: '100%',
              padding: '1.75rem',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.25)',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                backgroundColor: '#FEF3C7',
                color: '#D97706',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
              }}
            >
              <AlertTriangle size={26} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '0.5rem', color: '#111827' }}>
              Replace items in your cart?
            </h3>
            <p style={{ color: '#6B7280', fontSize: '0.925rem', lineHeight: '1.5', marginBottom: '1.5rem' }}>
              Your cart currently contains dishes from <strong>{cartRestaurant?.name}</strong>. Adding this item from <strong>{conflictModal.newRestaurant?.name}</strong> will discard your existing selection.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <Button variant="secondary" onClick={cancelRestaurantSwitch}>
                Keep Current Cart
              </Button>
              <Button variant="primary" onClick={confirmRestaurantSwitch}>
                Start New Order
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
