import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Package,
  MapPin,
  Phone,
  CheckCircle2,
  AlertCircle,
  Clock,
  ArrowRight,
  DollarSign,
  Bike,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import deliveryService from '../../services/deliveryService';
import DeliverySidebar from '../../components/navigation/DeliverySidebar';
import Button from '../../components/common/Button';
import './Delivery.scss';

export default function DeliveryActivePage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [activeDelivery, setActiveDelivery] = useState(null);
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState({ availability_status: 'BUSY', available_requests_count: 0 });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // COD Modal State
  const [showCODModal, setShowCODModal] = useState(false);
  const [codConfirmed, setCodConfirmed] = useState(false);

  const fetchActiveDelivery = async () => {
    try {
      const [activeData, profData, statsData] = await Promise.all([
        deliveryService.getActiveDelivery(),
        deliveryService.getProfile(),
        deliveryService.getDashboardStatistics(),
      ]);
      setActiveDelivery(activeData);
      setProfile(profData);
      setStats(statsData);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to load active delivery task.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveDelivery();
    const interval = setInterval(fetchActiveDelivery, 10000);
    return () => clearInterval(interval);
  }, []);

  const handlePickup = async () => {
    if (!activeDelivery) return;
    setActionLoading(true);
    setErrorMsg('');
    try {
      const updated = await deliveryService.confirmPickup(activeDelivery.order_id);
      setActiveDelivery(updated);
      setSuccessMsg('Order package confirmed as picked up from the restaurant.');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to confirm pickup.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStartDelivery = async () => {
    if (!activeDelivery) return;
    setActionLoading(true);
    setErrorMsg('');
    try {
      const updated = await deliveryService.startDelivery(activeDelivery.order_id);
      setActiveDelivery(updated);
      setSuccessMsg('You are now out for delivery! Head towards the customer dorm.');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to start delivery.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCompleteDelivery = async () => {
    if (!activeDelivery) return;
    setActionLoading(true);
    setErrorMsg('');
    try {
      await deliveryService.completeDelivery(activeDelivery.order_id, {
        confirm_delivered: true,
        confirm_cash_collected: activeDelivery.payment_method === 'CASH_ON_DELIVERY' ? true : undefined,
        collected_amount: activeDelivery.payment_method === 'CASH_ON_DELIVERY' ? activeDelivery.total_amount : undefined,
      });
      setShowCODModal(false);
      setSuccessMsg('Delivery completed successfully! Great job.');
      setTimeout(() => {
        navigate('/delivery/dashboard');
      }, 1500);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to complete delivery.');
    } finally {
      setActionLoading(false);
    }
  };

  // Determine current stepper stage (1 to 4)
  const getStepperIndex = () => {
    if (!activeDelivery) return 0;
    const status = activeDelivery.order_status;
    if (status === 'READY_FOR_PICKUP') return 1;
    if (status === 'PICKED_UP') return 2;
    if (status === 'OUT_FOR_DELIVERY') return 3;
    if (status === 'DELIVERED') return 4;
    return 1;
  };

  const stepIdx = getStepperIndex();

  return (
    <div className="delivery-layout">
      <DeliverySidebar
        courierName={user?.full_name}
        vehicleType={profile?.vehicle_type || 'BICYCLE'}
        availabilityStatus={stats.availability_status}
        activeCount={activeDelivery ? 1 : 0}
        availableCount={stats.available_requests_count}
      />

      <main className="delivery-layout__content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1F2937' }}>
              Active Delivery Task
            </h1>
            <p style={{ color: '#6B7280', fontSize: '0.95rem' }}>
              Manage pickup, customer dropoff, and cash collection for your current run
            </p>
          </div>
          <Button variant="secondary" size="sm" icon={RefreshCw} onClick={fetchActiveDelivery} disabled={loading}>
            Refresh Status
          </Button>
        </div>

        {errorMsg && (
          <div className="auth-card__alert auth-card__alert--error" style={{ marginBottom: '1.5rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div className="auth-card__alert auth-card__alert--success" style={{ marginBottom: '1.5rem' }}>
            <CheckCircle2 size={18} />
            <span>{successMsg}</span>
          </div>
        )}

        {!activeDelivery ? (
          <div
            style={{
              background: '#FFFFFF',
              border: '1px solid #E5E7EB',
              borderRadius: '12px',
              padding: '3.5rem 1rem',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: '#ECFDF5',
                color: '#10B981',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem',
              }}
            >
              <CheckCircle2 size={30} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.35rem' }}>
              No active delivery task in progress
            </h3>
            <p style={{ color: '#6B7280', fontSize: '0.95rem', maxWidth: '440px', margin: '0 auto 1.5rem' }}>
              You are currently idle and ready to take on new campus orders. Claim an available order to get started!
            </p>
            <Link to="/delivery/available-orders">
              <Button variant="primary" size="md" icon={ArrowRight}>
                View Available Runs
              </Button>
            </Link>
          </div>
        ) : (
          <div>
            {/* Stepper Progress Bar */}
            <div
              style={{
                background: '#FFFFFF',
                border: '1px solid #E5E7EB',
                borderRadius: '12px',
                padding: '1.5rem',
                marginBottom: '2rem',
              }}
            >
              <div className="delivery-stepper">
                <div className={`delivery-stepper__step ${stepIdx >= 1 ? (stepIdx > 1 ? 'delivery-stepper__step--completed' : 'delivery-stepper__step--active') : ''}`}>
                  <div className="step-circle">{stepIdx > 1 ? <CheckCircle2 size={18} /> : '1'}</div>
                  <span className="step-label">Assigned</span>
                </div>
                <div className={`delivery-stepper__step ${stepIdx >= 2 ? (stepIdx > 2 ? 'delivery-stepper__step--completed' : 'delivery-stepper__step--active') : ''}`}>
                  <div className="step-circle">{stepIdx > 2 ? <CheckCircle2 size={18} /> : '2'}</div>
                  <span className="step-label">Picked Up</span>
                </div>
                <div className={`delivery-stepper__step ${stepIdx >= 3 ? (stepIdx > 3 ? 'delivery-stepper__step--completed' : 'delivery-stepper__step--active') : ''}`}>
                  <div className="step-circle">{stepIdx > 3 ? <CheckCircle2 size={18} /> : '3'}</div>
                  <span className="step-label">Out for Delivery</span>
                </div>
                <div className={`delivery-stepper__step ${stepIdx >= 4 ? 'delivery-stepper__step--completed' : ''}`}>
                  <div className="step-circle">{stepIdx >= 4 ? <CheckCircle2 size={18} /> : '4'}</div>
                  <span className="step-label">Delivered</span>
                </div>
              </div>
            </div>

            {/* Main Details Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
              {/* Restaurant Pickup Card */}
              <div style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem', color: '#EA580C' }}>
                  <MapPin size={20} />
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#1F2937' }}>Restaurant Pickup</h3>
                </div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1F2937', marginBottom: '0.2rem' }}>
                  {activeDelivery.restaurant_name}
                </h4>
                <p style={{ color: '#4B5563', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                  {activeDelivery.restaurant_address}
                </p>
                {activeDelivery.restaurant_phone && (
                  <a
                    href={`tel:${activeDelivery.restaurant_phone}`}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      color: '#EA580C',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      textDecoration: 'none',
                      marginBottom: '1rem',
                    }}
                  >
                    <Phone size={14} /> Call Kitchen ({activeDelivery.restaurant_phone})
                  </a>
                )}

                <div style={{ borderTop: '1px solid #F3F4F6', paddingTop: '1rem' }}>
                  <h5 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700, marginBottom: '0.5rem' }}>
                    Items to Collect ({activeDelivery.item_count})
                  </h5>
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {activeDelivery.items?.map((it, idx) => (
                      <li key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', fontSize: '0.9rem' }}>
                        <span><strong>{it.quantity}x</strong> {it.item_name}</span>
                        <span style={{ color: '#6B7280' }}>${it.total_price}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Customer Delivery Card */}
              <div style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem', color: '#10B981' }}>
                  <MapPin size={20} />
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#1F2937' }}>Customer Dropoff</h3>
                </div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1F2937', marginBottom: '0.2rem' }}>
                  {activeDelivery.customer_name}
                </h4>
                <p style={{ color: '#4B5563', fontSize: '0.9rem', marginBottom: '0.75rem', fontWeight: 500 }}>
                  {activeDelivery.delivery_address}
                </p>
                {activeDelivery.customer_phone && (
                  <a
                    href={`tel:${activeDelivery.customer_phone}`}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      color: '#10B981',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      textDecoration: 'none',
                      marginBottom: '1rem',
                    }}
                  >
                    <Phone size={14} /> Call Customer ({activeDelivery.customer_phone})
                  </a>
                )}

                <div style={{ borderTop: '1px solid #F3F4F6', paddingTop: '1rem' }}>
                  <h5 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700, marginBottom: '0.5rem' }}>
                    Payment Summary
                  </h5>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', fontSize: '0.9rem' }}>
                    <span style={{ color: '#6B7280' }}>Payment Method:</span>
                    <strong>{activeDelivery.payment_method}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                    <span style={{ color: '#6B7280' }}>Total Amount:</span>
                    <strong style={{ fontSize: '1.15rem', color: '#1F2937' }}>${activeDelivery.total_amount}</strong>
                  </div>
                  <div style={{ marginTop: '0.5rem' }}>
                    {activeDelivery.cod_collected ? (
                      <span className="badge badge--success">✓ Cash Collected</span>
                    ) : (
                      <span className="badge badge--warning">⚠ Cash Collection Required</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Contextual Action Bar */}
            <div
              style={{
                background: '#FFFFFF',
                border: '1px solid #E5E7EB',
                borderRadius: '12px',
                padding: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '1rem',
                marginBottom: '2rem',
              }}
            >
              <div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#1F2937' }}>
                  Next Required Action:
                </h4>
                <p style={{ color: '#6B7280', fontSize: '0.9rem' }}>
                  {activeDelivery.order_status === 'READY_FOR_PICKUP' &&
                    'Collect the sealed package from the kitchen and confirm below.'}
                  {activeDelivery.order_status === 'PICKED_UP' &&
                    'Start your campus run towards the student dorm.'}
                  {activeDelivery.order_status === 'OUT_FOR_DELIVERY' &&
                    'Meet customer at dorm location, collect payment (if COD), and complete handover.'}
                </p>
              </div>

              <div>
                {activeDelivery.order_status === 'READY_FOR_PICKUP' && (
                  <Button variant="primary" size="md" onClick={handlePickup} disabled={actionLoading}>
                    {actionLoading ? 'Confirming...' : 'Confirm Restaurant Pickup'}
                  </Button>
                )}

                {activeDelivery.order_status === 'PICKED_UP' && (
                  <Button variant="primary" size="md" onClick={handleStartDelivery} disabled={actionLoading}>
                    {actionLoading ? 'Starting...' : 'Depart & Start Delivery Run'}
                  </Button>
                )}

                {activeDelivery.order_status === 'OUT_FOR_DELIVERY' && (
                  <Button
                    variant="primary"
                    size="md"
                    onClick={() => {
                      if (activeDelivery.payment_method === 'CASH_ON_DELIVERY' && !activeDelivery.cod_collected) {
                        setShowCODModal(true);
                      } else {
                        handleCompleteDelivery();
                      }
                    }}
                    disabled={actionLoading}
                  >
                    {actionLoading ? 'Completing...' : 'Complete Delivery Run'}
                  </Button>
                )}
              </div>
            </div>

            {/* Chronological Audit Timeline */}
            <div style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '1.5rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#1F2937', marginBottom: '1rem' }}>
                Order Lifecycle Timeline
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {activeDelivery.status_history?.map((h, i) => (
                  <div key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#F97316', marginTop: '6px' }} />
                    <div>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.9rem', color: '#1F2937' }}>{h.new_status}</span>
                        <span style={{ fontSize: '0.75rem', color: '#6B7280' }}>
                          {new Date(h.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </span>
                      </div>
                      {h.notes && <p style={{ fontSize: '0.825rem', color: '#4B5563', margin: 0 }}>{h.notes}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* COD Confirmation Modal */}
        {showCODModal && activeDelivery && (
          <div className="delivery-modal-overlay">
            <div className="delivery-modal">
              <div className="delivery-modal__header">
                <div className="delivery-modal__icon">
                  <DollarSign size={24} />
                </div>
                <div>
                  <h3 className="delivery-modal__title">Confirm Cash on Delivery</h3>
                  <p style={{ fontSize: '0.85rem', color: '#6B7280' }}>
                    Cash payment verification before completing delivery
                  </p>
                </div>
              </div>

              <div className="delivery-modal__amount-box">
                <p className="amount-label">Payable Cash Total</p>
                <h2 className="amount-val">${activeDelivery.total_amount}</h2>
              </div>

              <label className="delivery-modal__checkbox">
                <input
                  type="checkbox"
                  checked={codConfirmed}
                  onChange={(e) => setCodConfirmed(e.target.checked)}
                />
                <span>
                  I confirm that I have physically received <strong>${activeDelivery.total_amount}</strong> in cash from the customer.
                </span>
              </label>

              <div className="delivery-modal__actions">
                <Button variant="secondary" size="md" onClick={() => setShowCODModal(false)} disabled={actionLoading}>
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="md"
                  onClick={handleCompleteDelivery}
                  disabled={!codConfirmed || actionLoading}
                >
                  {actionLoading ? 'Processing...' : 'Confirm Cash & Complete Delivery'}
                </Button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

