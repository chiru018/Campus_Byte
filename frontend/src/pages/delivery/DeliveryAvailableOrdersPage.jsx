import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Navigation,
  MapPin,
  Package,
  Clock,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import deliveryService from '../../services/deliveryService';
import DeliverySidebar from '../../components/navigation/DeliverySidebar';
import Button from '../../components/common/Button';
import './Delivery.scss';

export default function DeliveryAvailableOrdersPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [stats, setStats] = useState({ availability_status: 'AVAILABLE', active_delivery_count: 0 });
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [acceptingId, setAcceptingId] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const fetchOrders = async () => {
    setErrorMsg('');
    try {
      const [statsData, profData] = await Promise.all([
        deliveryService.getDashboardStatistics(),
        deliveryService.getProfile(),
      ]);
      setStats(statsData);
      setProfile(profData);

      if (statsData.availability_status === 'AVAILABLE') {
        const res = await deliveryService.getAvailableOrders(page, 20);
        setOrders(res.orders || []);
        setTotal(res.total || 0);
      } else {
        setOrders([]);
        setTotal(0);
      }
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to load available orders.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 12000);
    return () => clearInterval(interval);
  }, [page]);

  const handleGoAvailable = async () => {
    try {
      await deliveryService.updateAvailability('AVAILABLE');
      await fetchOrders();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to update status.');
    }
  };

  const handleAcceptOrder = async (orderId) => {
    setAcceptingId(orderId);
    setErrorMsg('');
    try {
      await deliveryService.acceptOrder(orderId);
      navigate('/delivery/active-delivery');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Order already claimed or unavailable.');
      await fetchOrders();
    } finally {
      setAcceptingId(null);
    }
  };

  return (
    <div className="delivery-layout">
      <DeliverySidebar
        courierName={user?.full_name}
        vehicleType={profile?.vehicle_type || 'BICYCLE'}
        availabilityStatus={stats.availability_status}
        activeCount={stats.active_delivery_count}
        availableCount={total}
      />

      <main className="delivery-layout__content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1F2937' }}>
              Available Delivery Runs
            </h1>
            <p style={{ color: '#6B7280', fontSize: '0.95rem' }}>
              Real-time feed of campus dining orders prepared and waiting for courier collection
            </p>
          </div>
          <Button variant="secondary" size="sm" icon={RefreshCw} onClick={fetchOrders} disabled={loading}>
            Refresh
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

        {stats.availability_status !== 'AVAILABLE' && (
          <div
            style={{
              background: '#FFF7ED',
              border: '1px solid #FED7AA',
              borderRadius: '12px',
              padding: '1.25rem',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div>
              <h4 style={{ fontWeight: 700, color: '#9A3412', marginBottom: '0.2rem' }}>
                You are currently OFFLINE
              </h4>
              <p style={{ fontSize: '0.875rem', color: '#C2410C' }}>
                Switch your status to AVAILABLE to view and accept campus delivery runs.
              </p>
            </div>
            <Button variant="primary" size="sm" onClick={handleGoAvailable}>
              Go Available
            </Button>
          </div>
        )}

        {stats.active_delivery_count > 0 && (
          <div
            style={{
              background: '#EFF6FF',
              border: '1px solid #BFDBFE',
              borderRadius: '12px',
              padding: '1rem 1.25rem',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '0.75rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#1E40AF' }}>
              <Package size={18} />
              <span>You currently have an active delivery assignment in progress.</span>
            </div>
            <Button variant="outline" size="sm" onClick={() => navigate('/delivery/active-delivery')}>
              Go to Active Run
            </Button>
          </div>
        )}

        {orders.length === 0 ? (
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
                background: '#F3F4F6',
                color: '#9CA3AF',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem',
              }}
            >
              <Navigation size={28} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.35rem' }}>
              No available delivery requests right now
            </h3>
            <p style={{ color: '#6B7280', fontSize: '0.925rem', maxWidth: '420px', margin: '0 auto' }}>
              All ready orders have been assigned to couriers. This feed automatically polls for newly prepared orders every 12 seconds.
            </p>
          </div>
        ) : (
          <div className="available-orders-grid">
            {orders.map((ord) => (
              <div key={ord.order_id} className="available-order-card">
                <div>
                  <div className="available-order-card__top">
                    <div>
                      <h3 className="available-order-card__rest-name">{ord.restaurant_name}</h3>
                      <p className="available-order-card__rest-addr">
                        <MapPin size={13} /> {ord.restaurant_address}
                      </p>
                    </div>
                    <span className="badge badge--success">Ready</span>
                  </div>

                  <div className="available-order-card__summary">
                    <div className="items-title">
                      <Package size={14} /> Destination: {ord.delivery_area}
                    </div>
                    <p style={{ margin: '0.35rem 0', fontWeight: 500 }}>{ord.items_summary}</p>
                    <p style={{ fontSize: '0.75rem', color: '#6B7280' }}>
                      <Clock size={11} style={{ display: 'inline', marginRight: '3px' }} />
                      Placed {new Date(ord.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>

                <div className="available-order-card__footer">
                  <div>
                    <span className="available-order-card__price">${ord.total_amount}</span>
                    <span className="badge badge--info" style={{ marginLeft: '0.4rem', fontSize: '0.7rem' }}>
                      {ord.payment_method}
                    </span>
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleAcceptOrder(ord.order_id)}
                    disabled={acceptingId === ord.order_id || stats.active_delivery_count > 0}
                  >
                    {acceptingId === ord.order_id ? 'Claiming...' : 'Accept Delivery'}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
