import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  CheckCircle,
  PackageCheck,
  ChefHat,
  Bike,
  Home,
  XCircle,
  AlertTriangle,
  MapPin,
  Banknote,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import orderService from '../../services/orderService';
import Button from '../../components/common/Button';
import './Orders.scss';

const ACTIVE_STATUSES = [
  'PENDING',
  'ACCEPTED',
  'PREPARING',
  'READY_FOR_PICKUP',
  'PICKED_UP',
  'OUT_FOR_DELIVERY',
];

const STAGES = [
  { key: 'PENDING', label: 'Order Placed', desc: 'Sent to restaurant', icon: Clock },
  { key: 'ACCEPTED', label: 'Order Accepted', desc: 'Kitchen acknowledged order', icon: CheckCircle },
  { key: 'PREPARING', label: 'Preparing Food', desc: 'Freshly cooking your meal', icon: ChefHat },
  { key: 'READY_FOR_PICKUP', label: 'Ready for Pickup', desc: 'Prepared & awaiting courier', icon: PackageCheck },
  { key: 'PICKED_UP', label: 'Order Picked Up', desc: 'Courier collected meal from kitchen', icon: PackageCheck },
  { key: 'OUT_FOR_DELIVERY', label: 'Out for Delivery', desc: 'Campus courier en route to dorm', icon: Bike },
  { key: 'DELIVERED', label: 'Delivered', desc: 'Handed over at your campus room', icon: Home },
];

export default function OrderTrackingPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  // Cancellation Modal State
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState('');

  const fetchOrderDetails = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    try {
      const data = await orderService.getOrderById(orderId);
      setOrder(data);
      setErrorMsg('');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Unable to retrieve order details.');
    } finally {
      setLoading(false);
      if (isManual) setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchOrderDetails();
  }, [orderId]);

  // Polling for live status updates if order is in progress
  useEffect(() => {
    if (!order) return;
    if (!ACTIVE_STATUSES.includes(order.order_status)) return;

    const interval = setInterval(() => {
      fetchOrderDetails();
    }, 12000); // Poll every 12 seconds

    return () => clearInterval(interval);
  }, [order?.order_status, orderId]);

  const handleCancelOrder = async () => {
    setCancelling(true);
    setCancelError('');
    try {
      const updated = await orderService.cancelOrder(orderId, cancelReason);
      setOrder(updated);
      setShowCancelModal(false);
    } catch (err) {
      setCancelError(err.response?.data?.detail || 'Failed to cancel order.');
    } finally {
      setCancelling(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '6rem 0', minHeight: '60vh' }}>
        <p>Retrieving live order tracking...</p>
      </div>
    );
  }

  if (errorMsg || !order) {
    return (
      <div className="orders-page">
        <div className="container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <h2>Order Not Found</h2>
          <p style={{ color: '#64748B', marginBottom: '2rem' }}>
            {errorMsg || 'We could not find the requested order.'}
          </p>
          <Link to="/my-orders">
            <Button variant="primary" icon={ArrowLeft}>
              Back to My Orders
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const isCancelled = order.order_status === 'CANCELLED' || order.order_status === 'REJECTED';
  const isPending = order.order_status === 'PENDING';

  // Calculate timeline stage index
  const stageOrder = [
    'PENDING',
    'ACCEPTED',
    'PREPARING',
    'READY_FOR_PICKUP',
    'PICKED_UP',
    'OUT_FOR_DELIVERY',
    'DELIVERED',
  ];
  const currentStageIndex = stageOrder.indexOf(order.order_status);

  return (
    <div className="orders-page">
      <div className="container">
        {/* Header */}
        <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <Link to="/my-orders" className="back-btn">
              <ArrowLeft size={16} /> All Orders
            </Link>
            <h1>Order #{order.id.substring(0, 8).toUpperCase()}</h1>
            <p>
              From <strong>{order.restaurant_name || 'Campus Outlet'}</strong> • Placed on{' '}
              {new Date(order.created_at).toLocaleDateString([], {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button
              type="button"
              onClick={() => fetchOrderDetails(true)}
              disabled={refreshing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                background: '#FFFFFF',
                border: '1px solid #CBD5E1',
                borderRadius: '0.5rem',
                padding: '0.5rem 0.85rem',
                fontSize: '0.875rem',
                fontWeight: '600',
                color: '#475569',
                cursor: 'pointer',
              }}
            >
              <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>

            {isPending && (
              <Button
                variant="danger"
                size="small"
                onClick={() => setShowCancelModal(true)}
              >
                Cancel Order
              </Button>
            )}
          </div>
        </div>

        {/* Cancellation / Rejection Notice Banner */}
        {isCancelled && (
          <div className="cancelled-banner">
            <XCircle size={28} style={{ flexShrink: 0 }} />
            <div>
              <h3>
                {order.order_status === 'REJECTED'
                  ? 'Order Rejected by Restaurant'
                  : 'This order has been cancelled'}
              </h3>
              <p>
                {order.order_status === 'REJECTED' ? (
                  <>
                    <span><strong>Reason:</strong> {order.rejection_reason || 'The restaurant was unable to fulfill this order.'}</span>
                    {order.rejected_at && (
                      <span style={{ display: 'block', marginTop: '0.25rem', fontSize: '0.8rem', opacity: 0.85 }}>
                        Rejected at {new Date(order.rejected_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    )}
                  </>
                ) : (
                  'You have cancelled this order. No payment was charged.'
                )}
              </p>
            </div>
          </div>
        )}

        <div className="tracking-grid">
          {/* Left: Progress Timeline */}
          <div className="timeline-card">
            <div className="timeline-title">
              <h2>Delivery Progress</h2>
              <span className={`status-pill ${order.order_status.toLowerCase()}`}>
                {order.order_status}
              </span>
            </div>

            <div className="timeline-steps">
              {STAGES.map((stage, idx) => {
                const IconComponent = stage.icon;
                const isCompleted = !isCancelled && currentStageIndex > idx;
                const isCurrent = !isCancelled && currentStageIndex === idx;

                let stepClass = '';
                if (isCompleted) stepClass = 'completed';
                else if (isCurrent) stepClass = 'current';

                // Look up timestamp from status_history
                const historyMatch = order.status_history?.find(
                  (h) => h.new_status === stage.key
                );

                return (
                  <div key={stage.key} className={`timeline-step ${stepClass}`}>
                    <div className="step-icon">
                      <IconComponent size={18} />
                    </div>
                    <div className="step-content">
                      <h4>{stage.label}</h4>
                      <p>{stage.desc}</p>
                      {historyMatch && (
                        <div className="step-time">
                          {new Date(historyMatch.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: Order Summary & Delivery Details */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Courier Info Card (shown when assigned) */}
            {order.delivery_partner_name && (
              <div
                style={{
                  background: 'linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%)',
                  borderRadius: '1rem',
                  border: '1px solid #FED7AA',
                  padding: '1.25rem',
                  boxShadow: '0 2px 6px rgba(249, 115, 22, 0.08)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <Bike size={20} color="#EA580C" />
                  <h3 style={{ fontSize: '1rem', fontWeight: '800', color: '#9A3412', margin: 0 }}>
                    Assigned Campus Courier
                  </h3>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <div>
                    <h4 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#1F2937', margin: '0 0 0.15rem' }}>
                      {order.delivery_partner_name}
                    </h4>
                    <p style={{ fontSize: '0.85rem', color: '#C2410C', margin: 0 }}>
                      Mode: {order.delivery_partner_vehicle || 'Bicycle'}
                    </p>
                  </div>
                  {order.delivery_partner_phone && (
                    <a
                      href={`tel:${order.delivery_partner_phone}`}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        background: '#EA580C',
                        color: '#FFFFFF',
                        padding: '0.45rem 0.85rem',
                        borderRadius: '0.5rem',
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        textDecoration: 'none',
                      }}
                    >
                      Call Courier
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Delivery Location Card */}
            <div
              style={{
                background: '#FFFFFF',
                borderRadius: '1rem',
                border: '1px solid #E2E8F0',
                padding: '1.5rem',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <MapPin size={18} color="#F59E0B" />
                <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#1E293B', margin: 0 }}>
                  Delivery Destination
                </h3>
              </div>
              <p style={{ fontSize: '0.9rem', color: '#475569', margin: 0, lineHeight: '1.5' }}>
                {order.delivery_address}
              </p>
            </div>

            {/* Payment Card */}
            <div
              style={{
                background: '#FFFFFF',
                borderRadius: '1rem',
                border: '1px solid #E2E8F0',
                padding: '1.5rem',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <Banknote size={18} color="#10B981" />
                <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#1E293B', margin: 0 }}>
                  Payment Method
                </h3>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.9rem', color: '#475569' }}>
                  Cash on Delivery
                </span>
                <span style={{ fontSize: '0.8rem', fontWeight: '700', color: '#B45309', background: '#FEF3C7', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                  {order.payment_status}
                </span>
              </div>
            </div>

            {/* Items Breakdown Card */}
            <div
              style={{
                background: '#FFFFFF',
                borderRadius: '1rem',
                border: '1px solid #E2E8F0',
                padding: '1.5rem',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
              }}
            >
              <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#1E293B', margin: '0 0 1rem' }}>
                Items Ordered ({order.order_items?.length || 0})
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
                {order.order_items?.map((item) => (
                  <div
                    key={item.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '0.875rem',
                      color: '#475569',
                    }}
                  >
                    <span>
                      {item.quantity}x {item.item_name}
                    </span>
                    <span style={{ fontWeight: '600', color: '#1E293B' }}>
                      ${parseFloat(item.total_price).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>

              <div style={{ borderTop: '1px dashed #E2E8F0', paddingTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: '#64748B' }}>
                  <span>Subtotal</span>
                  <span>${parseFloat(order.subtotal).toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: '#64748B' }}>
                  <span>Delivery Fee</span>
                  <span>${parseFloat(order.delivery_fee).toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1.15rem', fontWeight: '800', color: '#0F172A', marginTop: '0.5rem' }}>
                  <span>Total Amount</span>
                  <span style={{ color: '#F59E0B' }}>
                    ${parseFloat(order.total_amount).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cancel Order Modal */}
      {showCancelModal && (
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
              maxWidth: '440px',
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
                backgroundColor: '#FEE2E2',
                color: '#DC2626',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
              }}
            >
              <AlertTriangle size={24} />
            </div>

            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '0.5rem', color: '#111827' }}>
              Cancel this order?
            </h3>
            <p style={{ color: '#6B7280', fontSize: '0.925rem', lineHeight: '1.5', marginBottom: '1.25rem' }}>
              Are you sure you want to cancel your order from <strong>{order.restaurant_name}</strong>? Orders can only be cancelled while pending.
            </p>

            {cancelError && (
              <div style={{ color: '#DC2626', fontSize: '0.85rem', marginBottom: '1rem' }}>
                {cancelError}
              </div>
            )}

            <div style={{ marginBottom: '1.5rem', textAlign: 'left' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#475569', marginBottom: '0.35rem' }}>
                Cancellation Reason (Optional)
              </label>
              <input
                type="text"
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                placeholder="e.g. Changed my mind, placed by mistake"
                style={{
                  width: '100%',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '0.5rem',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.9rem',
                }}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <Button
                variant="secondary"
                onClick={() => setShowCancelModal(false)}
                disabled={cancelling}
              >
                Keep Order
              </Button>
              <Button
                variant="danger"
                onClick={handleCancelOrder}
                disabled={cancelling}
              >
                {cancelling ? (
                  <>
                    <Loader2 size={16} className="animate-spin" /> Cancelling...
                  </>
                ) : (
                  'Yes, Cancel Order'
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

