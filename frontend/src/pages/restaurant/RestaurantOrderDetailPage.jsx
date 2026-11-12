import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  CheckCircle,
  ChefHat,
  PackageCheck,
  XCircle,
  MapPin,
  Phone,
  User,
  Banknote,
  UtensilsCrossed,
  AlertTriangle,
  History,
  Store,
  Loader2,
} from 'lucide-react';
import restaurantOrderService from '../../services/restaurantOrderService';
import restaurantService from '../../services/restaurantService';
import RestaurantSidebar from '../../components/navigation/RestaurantSidebar';
import Button from '../../components/common/Button';
import './RestaurantOrders.scss';

const PRESET_REASONS = [
  'Kitchen capacity reached',
  'Ingredients temporarily out of stock',
  'Outlet closing early for maintenance',
  'Item customization not possible',
];

export default function RestaurantOrderDetailPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();

  const [restaurant, setRestaurant] = useState(null);
  const [order, setOrder] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Rejection Dialog State
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [rejectionError, setRejectionError] = useState('');
  const [rejectSubmitting, setRejectSubmitting] = useState(false);

  // Fetch Restaurant Profile & Order Data
  const fetchOrderData = async () => {
    setLoading(true);
    try {
      const [restData, orderData, historyData] = await Promise.all([
        restaurantService.getMyRestaurant(),
        restaurantOrderService.getOrderById(orderId),
        restaurantOrderService.getOrderHistory(orderId),
      ]);
      setRestaurant(restData);
      setOrder(orderData);
      setHistory(historyData);
      setErrorMsg('');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to retrieve order details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderData();
  }, [orderId]);

  // Action Handlers
  const handleAccept = async () => {
    setActionLoading(true);
    try {
      const updated = await restaurantOrderService.acceptOrder(orderId);
      setOrder(updated);
      const updatedHistory = await restaurantOrderService.getOrderHistory(orderId);
      setHistory(updatedHistory);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to accept order.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStartPrep = async () => {
    setActionLoading(true);
    try {
      const updated = await restaurantOrderService.startPreparation(orderId);
      setOrder(updated);
      const updatedHistory = await restaurantOrderService.getOrderHistory(orderId);
      setHistory(updatedHistory);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to start food preparation.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleMarkReady = async () => {
    setActionLoading(true);
    try {
      const updated = await restaurantOrderService.markReadyForPickup(orderId);
      setOrder(updated);
      const updatedHistory = await restaurantOrderService.getOrderHistory(orderId);
      setHistory(updatedHistory);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to mark ready for pickup.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleConfirmReject = async (e) => {
    e.preventDefault();
    if (!rejectionReason.trim() || rejectionReason.trim().length < 5) {
      setRejectionError('Rejection reason must be at least 5 characters long.');
      return;
    }

    setRejectSubmitting(true);
    setRejectionError('');
    try {
      const updated = await restaurantOrderService.rejectOrder(orderId, rejectionReason.trim());
      setOrder(updated);
      const updatedHistory = await restaurantOrderService.getOrderHistory(orderId);
      setHistory(updatedHistory);
      setShowRejectModal(false);
    } catch (err) {
      setRejectionError(err.response?.data?.detail || 'Failed to reject order.');
    } finally {
      setRejectSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '6rem 0', minHeight: '60vh' }}>
        <Loader2 size={36} className="animate-spin" color="#F59E0B" style={{ margin: '0 auto 1rem' }} />
        <p style={{ color: '#64748B' }}>Loading order details...</p>
      </div>
    );
  }

  if (errorMsg || !order) {
    return (
      <div className="restaurant-orders-page">
        <div className="container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <h2>Order Not Found</h2>
          <p style={{ color: '#64748B', marginBottom: '2rem' }}>
            {errorMsg || 'We could not locate the requested order.'}
          </p>
          <Link to="/restaurant/orders">
            <Button variant="primary" icon={ArrowLeft}>
              Back to Orders
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const isPending = order.order_status === 'PENDING';
  const isAccepted = order.order_status === 'ACCEPTED';
  const isPreparing = order.order_status === 'PREPARING';
  const isReady = order.order_status === 'READY_FOR_PICKUP';
  const isRejected = order.order_status === 'REJECTED';
  const isCancelled = order.order_status === 'CANCELLED';

  return (
    <div className="restaurant-orders-page">
      <div className="container">
        <div className="dashboard-layout">
          {/* Sidebar */}
          <RestaurantSidebar
            restaurantName={restaurant?.name}
            isOpen={restaurant?.is_open}
          />

          {/* Main Content */}
          <main className="dashboard-main">
            {/* Top Bar */}
            <div style={{ marginBottom: '1.5rem' }}>
              <Link
                to="/restaurant/orders"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  color: '#64748B',
                  textDecoration: 'none',
                  fontSize: '0.9rem',
                  fontWeight: '600',
                  marginBottom: '0.75rem',
                }}
              >
                <ArrowLeft size={16} /> Back to Live Orders
              </Link>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', margin: 0 }}>
                    Order #{order.id.substring(0, 8).toUpperCase()}
                  </h1>
                  <p style={{ color: '#64748B', fontSize: '0.9rem', margin: '0.25rem 0 0' }}>
                    Placed on {new Date(order.created_at).toLocaleString([], {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span className={`status-pill ${order.order_status.toLowerCase()}`}>
                    {order.order_status.replace(/_/g, ' ')}
                  </span>
                </div>
              </div>
            </div>

            {/* Rejection Notice Banner if applicable */}
            {isRejected && (
              <div
                style={{
                  backgroundColor: '#FEF2F2',
                  border: '1px solid #FECACA',
                  borderRadius: '0.75rem',
                  padding: '1.25rem',
                  marginBottom: '1.5rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem',
                  color: '#991B1B',
                }}
              >
                <XCircle size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong style={{ display: 'block', fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                    Order Rejected by Kitchen
                  </strong>
                  <span style={{ fontSize: '0.9rem' }}>
                    <strong>Reason:</strong> {order.rejection_reason || 'Kitchen unable to fulfill order'}
                  </span>
                </div>
              </div>
            )}

            {/* Two-Column Grid: Left (Details) / Right (Actions & Timeline) */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem', alignItems: 'start' }}>
              {/* Left Column */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {/* Customer Information Card */}
                <div
                  style={{
                    background: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '1rem',
                    padding: '1.5rem',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                  }}
                >
                  <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#1E293B', margin: '0 0 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <User size={18} color="#F59E0B" /> Customer & Delivery Details
                  </h3>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <span style={{ display: 'block', fontSize: '0.8rem', color: '#64748B', textTransform: 'uppercase', fontWeight: '700' }}>
                        Customer Name
                      </span>
                      <strong style={{ fontSize: '1rem', color: '#0F172A' }}>
                        {order.customer_name || 'Campus Student'}
                      </strong>
                    </div>

                    <div>
                      <span style={{ display: 'block', fontSize: '0.8rem', color: '#64748B', textTransform: 'uppercase', fontWeight: '700' }}>
                        Contact Phone
                      </span>
                      <strong style={{ fontSize: '1rem', color: '#0F172A' }}>
                        {order.customer_phone || 'Not provided'}
                      </strong>
                    </div>
                  </div>

                  <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px dashed #E2E8F0' }}>
                    <span style={{ display: 'block', fontSize: '0.8rem', color: '#64748B', textTransform: 'uppercase', fontWeight: '700', marginBottom: '0.25rem' }}>
                      Delivery Location (Hostel / Room / Notes)
                    </span>
                    <p style={{ margin: 0, fontSize: '0.925rem', color: '#334155', lineHeight: '1.5' }}>
                      📍 {order.delivery_address}
                    </p>
                  </div>

                  {/* Courier Assignment Section */}
                  {order.delivery_partner_id ? (
                    <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #F1F5F9' }}>
                      <span style={{ display: 'block', fontSize: '0.8rem', color: '#64748B', textTransform: 'uppercase', fontWeight: '700', marginBottom: '0.25rem' }}>
                        Assigned Campus Courier
                      </span>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <strong style={{ fontSize: '0.95rem', color: '#0F172A' }}>
                            {order.delivery_partner_name || 'Active Courier'}
                          </strong>
                          {order.delivery_partner_vehicle && (
                            <span style={{ fontSize: '0.825rem', color: '#64748B', marginLeft: '0.5rem' }}>
                              (Mode: {order.delivery_partner_vehicle})
                            </span>
                          )}
                        </div>
                        {order.delivery_partner_phone && (
                          <span style={{ fontSize: '0.85rem', color: '#F59E0B', fontWeight: 600 }}>
                            📞 {order.delivery_partner_phone}
                          </span>
                        )}
                      </div>
                    </div>
                  ) : (
                    order.order_status === 'READY_FOR_PICKUP' && (
                      <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #F1F5F9', color: '#D97706', fontSize: '0.875rem', fontWeight: 600 }}>
                        ⏳ Waiting for available campus delivery partner to accept pickup...
                      </div>
                    )
                  )}
                </div>

                {/* Food Items Ordered Table */}
                <div
                  style={{
                    background: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '1rem',
                    padding: '1.5rem',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                  }}
                >
                  <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#1E293B', margin: '0 0 1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <UtensilsCrossed size={18} color="#F59E0B" /> Food Items ({order.order_items?.length || 0})
                  </h3>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {order.order_items?.map((item) => (
                      <div
                        key={item.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          paddingBottom: '0.85rem',
                          borderBottom: '1px solid #F1F5F9',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                          <div
                            style={{
                              width: '48px',
                              height: '48px',
                              borderRadius: '0.5rem',
                              backgroundColor: '#F1F5F9',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              overflow: 'hidden',
                              flexShrink: 0,
                            }}
                          >
                            {item.image_url ? (
                              <img
                                src={item.image_url}
                                alt={item.item_name}
                                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                onError={(e) => { e.target.style.display = 'none'; }}
                              />
                            ) : (
                              <UtensilsCrossed size={20} color="#94A3B8" />
                            )}
                          </div>
                          <div>
                            <strong style={{ display: 'block', fontSize: '0.95rem', color: '#0F172A' }}>
                              {item.item_name}
                            </strong>
                            <span style={{ fontSize: '0.85rem', color: '#64748B' }}>
                              ${parseFloat(item.unit_price).toFixed(2)} x {item.quantity}
                            </span>
                          </div>
                        </div>

                        <div style={{ textAlign: 'right' }}>
                          <span style={{ fontWeight: '700', fontSize: '1rem', color: '#0F172A' }}>
                            ${parseFloat(item.total_price).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Payment Summary breakdown */}
                  <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px dashed #E2E8F0', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: '#64748B' }}>
                      <span>Subtotal</span>
                      <span>${parseFloat(order.subtotal).toFixed(2)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: '#64748B' }}>
                      <span>Campus Delivery Fee</span>
                      <span>${parseFloat(order.delivery_fee).toFixed(2)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1.2rem', fontWeight: '800', color: '#0F172A', marginTop: '0.5rem' }}>
                      <span>Total Amount (Cash on Delivery)</span>
                      <span style={{ color: '#F59E0B' }}>${parseFloat(order.total_amount).toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Actions & Audit Timeline */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {/* Contextual Action Card */}
                <div
                  style={{
                    background: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '1rem',
                    padding: '1.5rem',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                  }}
                >
                  <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#1E293B', margin: '0 0 1rem' }}>
                    Order Action
                  </h3>

                  {isPending && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      <Button
                        variant="primary"
                        onClick={handleAccept}
                        disabled={actionLoading}
                        style={{ width: '100%', justifyContent: 'center' }}
                      >
                        {actionLoading ? 'Accepting Order...' : 'Accept Order'}
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => setShowRejectModal(true)}
                        disabled={actionLoading}
                        style={{ width: '100%', justifyContent: 'center' }}
                      >
                        Reject Order
                      </Button>
                    </div>
                  )}

                  {isAccepted && (
                    <Button
                      variant="primary"
                      icon={ChefHat}
                      onClick={handleStartPrep}
                      disabled={actionLoading}
                      style={{ width: '100%', justifyContent: 'center' }}
                    >
                      {actionLoading ? 'Updating...' : 'Start Cooking Food'}
                    </Button>
                  )}

                  {isPreparing && (
                    <Button
                      variant="primary"
                      icon={PackageCheck}
                      onClick={handleMarkReady}
                      disabled={actionLoading}
                      style={{ width: '100%', justifyContent: 'center', backgroundColor: '#10B981', borderColor: '#10B981' }}
                    >
                      {actionLoading ? 'Updating...' : 'Mark Ready for Pickup'}
                    </Button>
                  )}

                  {isReady && (
                    <div
                      style={{
                        padding: '1rem',
                        backgroundColor: '#ECFDF5',
                        border: '1px solid #A7F3D0',
                        borderRadius: '0.5rem',
                        color: '#065F46',
                        fontSize: '0.9rem',
                        lineHeight: '1.4',
                      }}
                    >
                      <strong>Prepared & Packaged:</strong> This order is ready for delivery partner pickup (Phase 7).
                    </div>
                  )}

                  {(isRejected || isCancelled) && (
                    <div
                      style={{
                        padding: '1rem',
                        backgroundColor: '#FEF2F2',
                        border: '1px solid #FECACA',
                        borderRadius: '0.5rem',
                        color: '#991B1B',
                        fontSize: '0.9rem',
                      }}
                    >
                      This order is terminal ({order.order_status}). No further actions available.
                    </div>
                  )}
                </div>

                {/* Status Transition Audit Timeline */}
                <div
                  style={{
                    background: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '1rem',
                    padding: '1.5rem',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                  }}
                >
                  <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#1E293B', margin: '0 0 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <History size={18} color="#64748B" /> Status History
                  </h3>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative', paddingLeft: '1.5rem' }}>
                    <div
                      style={{
                        position: 'absolute',
                        left: '6px',
                        top: '8px',
                        bottom: '8px',
                        width: '2px',
                        backgroundColor: '#E2E8F0',
                      }}
                    />

                    {history.map((h, idx) => (
                      <div key={h.id} style={{ position: 'relative' }}>
                        <div
                          style={{
                            position: 'absolute',
                            left: '-1.5rem',
                            top: '4px',
                            width: '14px',
                            height: '14px',
                            borderRadius: '50%',
                            backgroundColor: idx === history.length - 1 ? '#F59E0B' : '#94A3B8',
                            border: '2px solid #FFFFFF',
                          }}
                        />
                        <div>
                          <strong style={{ fontSize: '0.9rem', color: '#0F172A' }}>
                            {h.new_status.replace(/_/g, ' ')}
                          </strong>
                          <span style={{ display: 'block', fontSize: '0.775rem', color: '#64748B' }}>
                            {new Date(h.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {h.changed_by_role || 'SYSTEM'}
                          </span>
                          {h.notes && (
                            <span style={{ display: 'block', fontSize: '0.8rem', color: '#475569', marginTop: '0.2rem', fontStyle: 'italic' }}>
                              "{h.notes}"
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>

      {/* Reject Order Modal */}
      {showRejectModal && (
        <div className="modal-overlay">
          <div className="rejection-modal">
            <div className="modal-header">
              <AlertTriangle size={24} />
              <h3>Reject Order #{order.id.substring(0, 8).toUpperCase()}</h3>
            </div>
            <p>
              Please enter the reason for rejecting this order. The customer will see this message.
            </p>

            <div className="preset-reasons">
              {PRESET_REASONS.map((reason) => (
                <button
                  key={reason}
                  type="button"
                  className={rejectionReason === reason ? 'active' : ''}
                  onClick={() => setRejectionReason(reason)}
                >
                  {reason}
                </button>
              ))}
            </div>

            <textarea
              placeholder="Enter rejection reason (minimum 5 characters)..."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
            />

            {rejectionError && <div className="error-msg">{rejectionError}</div>}

            <div className="modal-actions">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowRejectModal(false)}
                disabled={rejectSubmitting}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={handleConfirmReject}
                disabled={rejectSubmitting}
              >
                {rejectSubmitting ? 'Rejecting Order...' : 'Confirm Rejection'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

