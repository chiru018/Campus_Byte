import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShoppingBag,
  ArrowLeft,
  Trash2,
  Plus,
  Minus,
  ShieldCheck,
  ArrowRight,
  Store,
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import Button from '../../components/common/Button';
import './Cart.scss';

export default function CartPage() {
  const {
    restaurant,
    items,
    totalItems,
    subtotal,
    deliveryFee,
    totalAmount,
    updateQuantity,
    removeFromCart,
    clearCart,
  } = useCart();

  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  const handleProceedToCheckout = () => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/checkout');
    } else {
      navigate('/checkout');
    }
  };

  if (items.length === 0 || !restaurant) {
    return (
      <div className="cart-page">
        <div className="container">
          <div className="empty-cart-state">
            <div className="icon-wrapper">
              <ShoppingBag size={36} />
            </div>
            <h2>Your Cart is Empty</h2>
            <p>
              Looks like you haven't added any dishes yet. Explore our top campus restaurants and discover fresh meals ready for delivery!
            </p>
            <Link to="/restaurants">
              <Button variant="primary" icon={ArrowRight}>
                Explore Campus Restaurants
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <div className="container">
        {/* Header */}
        <div className="cart-header">
          <Link to={`/restaurants/${restaurant.id}`} className="back-btn">
            <ArrowLeft size={16} /> Back to {restaurant.name}
          </Link>
          <h1>Your Order Cart</h1>
          <p className="restaurant-subtext">
            Ordering from <strong>{restaurant.name}</strong> • {restaurant.address}
          </p>
        </div>

        {/* Cart Layout */}
        <div className="cart-grid">
          {/* Items Card */}
          <div className="cart-items-card">
            <div className="card-header">
              <h2>Order Items ({totalItems})</h2>
              <button
                type="button"
                className="clear-cart-btn"
                onClick={clearCart}
              >
                <Trash2 size={14} /> Clear Cart
              </button>
            </div>

            <div className="cart-items-list">
              {items.map((item) => (
                <div key={item.id} className="cart-item-row">
                  <div className="item-image">
                    {item.image_url ? (
                      <img
                        src={item.image_url}
                        alt={item.name}
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    ) : (
                      <Store size={24} color="#94A3B8" />
                    )}
                  </div>

                  <div className="item-info">
                    <h3>{item.name}</h3>
                    <div className="unit-price">${item.price.toFixed(2)} each</div>
                  </div>

                  <div className="qty-stepper">
                    <button
                      type="button"
                      aria-label="Decrease quantity"
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    >
                      <Minus size={14} color="#334155" />
                    </button>
                    <span className="qty-val">{item.quantity}</span>
                    <button
                      type="button"
                      aria-label="Increase quantity"
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    >
                      <Plus size={14} color="#334155" />
                    </button>
                  </div>

                  <div className="line-total">
                    ${(item.price * item.quantity).toFixed(2)}
                  </div>

                  <button
                    type="button"
                    className="remove-btn"
                    title="Remove item"
                    onClick={() => removeFromCart(item.id)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Bill Summary Card */}
          <div className="cart-summary-card">
            <h2>Payment Summary</h2>

            <div className="summary-rows">
              <div className="summary-row">
                <span>Items Subtotal</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div className="summary-row">
                <span>Campus Delivery Fee</span>
                <span>${deliveryFee.toFixed(2)}</span>
              </div>
              <div className="summary-row highlight">
                <span>Platform Discount</span>
                <span>Free Packaging</span>
              </div>
            </div>

            <div className="total-row">
              <span>To Pay</span>
              <span className="total-price">${totalAmount.toFixed(2)}</span>
            </div>

            <button
              type="button"
              className="checkout-btn"
              onClick={handleProceedToCheckout}
            >
              Proceed to Checkout <ArrowRight size={18} />
            </button>

            <div className="trust-badge">
              <ShieldCheck size={16} color="#10B981" />
              <span>Cash on Delivery • Direct to your dorm</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

