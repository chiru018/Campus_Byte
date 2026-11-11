import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  MapPin,
  Phone,
  User as UserIcon,
  Banknote,
  ShieldCheck,
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Loader2,
} from 'lucide-react';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import orderService from '../../services/orderService';
import Button from '../../components/common/Button';
import './Cart.scss';

export default function CheckoutPage() {
  const {
    restaurant,
    items,
    totalItems,
    subtotal,
    deliveryFee,
    totalAmount,
    clearCart,
  } = useCart();

  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Form State
  const [formData, setFormData] = useState({
    fullName: user?.full_name || '',
    phone: user?.phone_number || '',
    hostelOrBlock: '',
    roomNumber: '',
    landmark: '',
  });

  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // If cart is empty, redirect to cart page
  if (items.length === 0 || !restaurant) {
    return (
      <div className="cart-page">
        <div className="container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <h2>Your cart is empty</h2>
          <p style={{ color: '#64748B', marginBottom: '1.5rem' }}>
            Please add dishes from a campus restaurant before proceeding to checkout.
          </p>
          <Link to="/restaurants">
            <Button variant="primary">Browse Outlets</Button>
          </Link>
        </div>
      </div>
    );
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!formData.fullName.trim() || !formData.phone.trim()) {
      setErrorMessage('Please provide your full name and contact phone number.');
      return;
    }

    if (!formData.hostelOrBlock.trim() || !formData.roomNumber.trim()) {
      setErrorMessage('Please provide your campus building/hostel and room number.');
      return;
    }

    // Compose formatted delivery address
    const fullAddress = `${formData.hostelOrBlock.trim()}, Room ${formData.roomNumber.trim()}${
      formData.landmark.trim() ? ` (Near ${formData.landmark.trim()})` : ''
    } | Recipient: ${formData.fullName.trim()} (${formData.phone.trim()})`;

    // Generate idempotency token
    const idempotencyKey = `cb-order-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;

    const orderPayload = {
      restaurant_id: restaurant.id,
      delivery_address: fullAddress,
      payment_method: 'CASH_ON_DELIVERY',
      items: items.map((i) => ({
        menu_item_id: i.id,
        quantity: i.quantity,
      })),
      idempotency_key: idempotencyKey,
    };

    setSubmitting(true);
    try {
      const createdOrder = await orderService.createOrder(orderPayload);
      clearCart();
      navigate(`/order-confirmation/${createdOrder.id}`, {
        state: { order: createdOrder },
      });
    } catch (err) {
      console.error('Order placement failed:', err);
      const detail =
        err.response?.data?.detail ||
        'Failed to complete order. Please review your address or try again.';
      setErrorMessage(detail);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="cart-page">
      <div className="container">
        {/* Header */}
        <div className="cart-header">
          <Link to="/cart" className="back-btn">
            <ArrowLeft size={16} /> Back to Cart
          </Link>
          <h1>Secure Checkout</h1>
          <p className="restaurant-subtext">
            Finalize delivery details for your order from <strong>{restaurant.name}</strong>
          </p>
        </div>

        {errorMessage && (
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
              marginBottom: '1.5rem',
            }}
          >
            <AlertCircle size={20} style={{ flexShrink: 0 }} />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handlePlaceOrder}>
          <div className="cart-grid">
            {/* Left: Address & Payment Selection */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Delivery Address Card */}
              <div
                style={{
                  background: '#FFFFFF',
                  borderRadius: '1rem',
                  border: '1px solid #E2E8F0',
                  padding: '1.5rem',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
                  <MapPin size={20} color="#F59E0B" />
                  <h2 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#1E293B', margin: 0 }}>
                    Campus Delivery Address
                  </h2>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#475569', marginBottom: '0.35rem' }}>
                      Recipient Full Name *
                    </label>
                    <input
                      type="text"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleChange}
                      required
                      placeholder="e.g. John Doe"
                      style={{
                        width: '100%',
                        padding: '0.65rem 0.85rem',
                        borderRadius: '0.5rem',
                        border: '1px solid #CBD5E1',
                        fontSize: '0.95rem',
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#475569', marginBottom: '0.35rem' }}>
                      Contact Phone *
                    </label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      required
                      placeholder="e.g. +1 555 123 4567"
                      style={{
                        width: '100%',
                        padding: '0.65rem 0.85rem',
                        borderRadius: '0.5rem',
                        border: '1px solid #CBD5E1',
                        fontSize: '0.95rem',
                      }}
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#475569', marginBottom: '0.35rem' }}>
                      Hostel / Hall / Building Name *
                    </label>
                    <input
                      type="text"
                      name="hostelOrBlock"
                      value={formData.hostelOrBlock}
                      onChange={handleChange}
                      required
                      placeholder="e.g. Emerald Hall / Block B"
                      style={{
                        width: '100%',
                        padding: '0.65rem 0.85rem',
                        borderRadius: '0.5rem',
                        border: '1px solid #CBD5E1',
                        fontSize: '0.95rem',
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#475569', marginBottom: '0.35rem' }}>
                      Room Number *
                    </label>
                    <input
                      type="text"
                      name="roomNumber"
                      value={formData.roomNumber}
                      onChange={handleChange}
                      required
                      placeholder="e.g. 304"
                      style={{
                        width: '100%',
                        padding: '0.65rem 0.85rem',
                        borderRadius: '0.5rem',
                        border: '1px solid #CBD5E1',
                        fontSize: '0.95rem',
                      }}
                    />
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#475569', marginBottom: '0.35rem' }}>
                    Landmark or Delivery Instructions (Optional)
                  </label>
                  <input
                    type="text"
                    name="landmark"
                    value={formData.landmark}
                    onChange={handleChange}
                    placeholder="e.g. Near 2nd floor staircase, ring upon arrival"
                    style={{
                      width: '100%',
                      padding: '0.65rem 0.85rem',
                      borderRadius: '0.5rem',
                      border: '1px solid #CBD5E1',
                      fontSize: '0.95rem',
                    }}
                  />
                </div>
              </div>

              {/* Payment Method Card */}
              <div
                style={{
                  background: '#FFFFFF',
                  borderRadius: '1rem',
                  border: '1px solid #E2E8F0',
                  padding: '1.5rem',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
                  <Banknote size={20} color="#10B981" />
                  <h2 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#1E293B', margin: 0 }}>
                    Payment Option
                  </h2>
                </div>

                {/* Pre-selected Cash on Delivery */}
                <div
                  style={{
                    border: '2px solid #F59E0B',
                    borderRadius: '0.75rem',
                    padding: '1rem 1.25rem',
                    backgroundColor: '#FFFBEB',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                  }}
                >
                  <div
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      border: '6px solid #F59E0B',
                      backgroundColor: '#FFFFFF',
                    }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: '700', color: '#92400E', fontSize: '0.95rem' }}>
                      Cash on Delivery (COD)
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#B45309' }}>
                      Pay exact cash to our campus courier when your meal arrives at your room.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Order Summary Card */}
            <div className="cart-summary-card">
              <h2>Order Summary</h2>

              <div style={{ marginBottom: '1.25rem' }}>
                <div style={{ fontWeight: '600', color: '#1E293B', fontSize: '0.95rem', marginBottom: '0.75rem' }}>
                  {restaurant.name}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {items.map((i) => (
                    <div
                      key={i.id}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: '0.875rem',
                        color: '#64748B',
                      }}
                    >
                      <span>
                        {i.quantity}x {i.name}
                      </span>
                      <span style={{ fontWeight: '600', color: '#334155' }}>
                        ${(i.price * i.quantity).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="summary-rows">
                <div className="summary-row">
                  <span>Items Subtotal</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="summary-row">
                  <span>Campus Courier Fee</span>
                  <span>${deliveryFee.toFixed(2)}</span>
                </div>
              </div>

              <div className="total-row">
                <span>Total Amount</span>
                <span className="total-price">${totalAmount.toFixed(2)}</span>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="checkout-btn"
              >
                {submitting ? (
                  <>
                    <Loader2 size={18} className="animate-spin" /> Placing Order...
                  </>
                ) : (
                  <>Place Order (${totalAmount.toFixed(2)})</>
                )}
              </button>

              <div className="trust-badge">
                <Clock size={16} color="#64748B" />
                <span>Estimated preparation & delivery: 20–30 mins</span>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
