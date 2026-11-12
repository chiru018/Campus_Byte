import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Navigation,
  Package,
  CheckCircle2,
  DollarSign,
  Activity,
  ArrowRight,
  AlertCircle,
  MapPin,
  Clock,
  Bike,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import deliveryService from '../../services/deliveryService';
import DeliverySidebar from '../../components/navigation/DeliverySidebar';
import Button from '../../components/common/Button';
import './Delivery.scss';

export default function DeliveryDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    available_requests_count: 0,
    active_delivery_count: 0,
    completed_deliveries_count: 0,
    total_deliveries_count: 0,
    total_cod_collected: '0.00',
    availability_status: 'AVAILABLE',
  });
  const [profile, setProfile] = useState(null);
  const [activeDelivery, setActiveDelivery] = useState(null);
  const [availableOrders, setAvailableOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const loadData = async () => {
    try {
      const [statsData, profData, activeData] = await Promise.all([
        deliveryService.getDashboardStatistics(),
        deliveryService.getProfile(),
        deliveryService.getActiveDelivery(),
      ]);
      setStats(statsData);
      setProfile(profData);
      setActiveDelivery(activeData);

      if (statsData.availability_status === 'AVAILABLE') {
        const availData = await deliveryService.getAvailableOrders(1, 4);
        setAvailableOrders(availData.orders || []);
      } else {
        setAvailableOrders([]);
      }
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to load delivery data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Poll stats every 15 seconds
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleAvailabilityChange = async (newStatus) => {
    setToggling(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const updated = await deliveryService.updateAvailability(newStatus);
      setStats((prev) => ({ ...prev, availability_status: updated.availability_status }));
      setSuccessMsg(`Availability updated to ${newStatus}`);
      await loadData();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to update availability.');
    } finally {
      setToggling(false);
    }
  };

  const handleClaimOrder = async (orderId) => {
    try {
      await deliveryService.acceptOrder(orderId);
      navigate('/delivery/active-delivery');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Order already claimed or unavailable.');
      loadData();
    }
  };

  return (
    <div className="delivery-layout">
      <DeliverySidebar
        courierName={user?.full_name}
        vehicleType={profile?.vehicle_type || 'BICYCLE'}
        availabilityStatus={stats.availability_status}
        activeCount={stats.active_delivery_count}
        availableCount={stats.available_requests_count}
      />

      <main className="delivery-layout__content">
        {/* Alerts */}
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

        {/* Availability Control Bar */}
        <div className="availability-bar">
          <div className="availability-bar__status-group">
            <Activity size={22} color="#F97316" />
            <div>
              <h3 className="availability-bar__title">Courier Status</h3>
              <p style={{ fontSize: '0.825rem', color: '#6B7280' }}>
                Manage whether you can receive and claim campus run assignments
              </p>
            </div>
          </div>
          <div className="availability-bar__btn-group">
            <button
              className={`button button--sm ${
                stats.availability_status === 'AVAILABLE' ? 'button--primary' : 'button--outline'
              }`}
              onClick={() => handleAvailabilityChange('AVAILABLE')}
              disabled={toggling || stats.availability_status === 'AVAILABLE'}
            >
              🟢 Go Available
            </button>
            <button
              className={`button button--sm ${
                stats.availability_status === 'OFFLINE' ? 'button--secondary' : 'button--outline'
              }`}
              onClick={() => handleAvailabilityChange('OFFLINE')}
              disabled={toggling || stats.availability_status === 'OFFLINE' || stats.active_delivery_count > 0}
            >
              ⚪ Go Offline
            </button>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="delivery-metrics-grid">
          <div className="delivery-metric-card">
            <div className="delivery-metric-card__icon delivery-metric-card__icon--orange">
              <Navigation size={24} />
            </div>
            <div>
              <p className="delivery-metric-card__label">Available Runs</p>
              <h2 className="delivery-metric-card__value">{stats.available_requests_count}</h2>
            </div>
          </div>

          <div className="delivery-metric-card">
            <div className="delivery-metric-card__icon delivery-metric-card__icon--blue">
              <Package size={24} />
            </div>
            <div>
              <p className="delivery-metric-card__label">Active Task</p>
              <h2 className="delivery-metric-card__value">
                {stats.active_delivery_count > 0 ? '1 In-Flight' : 'Idle'}
              </h2>
            </div>
          </div>

          <div className="delivery-metric-card">
            <div className="delivery-metric-card__icon delivery-metric-card__icon--green">
              <CheckCircle2 size={24} />
            </div>
            <div>
              <p className="delivery-metric-card__label">Delivered Runs</p>
              <h2 className="delivery-metric-card__value">{stats.completed_deliveries_count}</h2>
            </div>
          </div>

          <div className="delivery-metric-card">
            <div className="delivery-metric-card__icon delivery-metric-card__icon--purple">
              <DollarSign size={24} />
            </div>
            <div>
              <p className="delivery-metric-card__label">COD Collected</p>
              <h2 className="delivery-metric-card__value">${stats.total_cod_collected}</h2>
            </div>
          </div>
        </div>

        {/* Active Delivery Spotlight */}
        {activeDelivery ? (
          <div className="active-delivery-card">
            <div className="active-delivery-card__header">
              <div className="active-delivery-card__title">
                <Package size={22} />
                <span>Active Run: Order #{activeDelivery.order_id.slice(0, 8)}</span>
              </div>
              <span className="badge badge--warning">{activeDelivery.order_status}</span>
            </div>

            <div className="active-delivery-card__locations">
              <div className="active-delivery-card__loc-item">
                <h4>
                  <MapPin size={14} /> Pickup Kitchen
                </h4>
                <p>{activeDelivery.restaurant_name}</p>
                <span>{activeDelivery.restaurant_address}</span>
              </div>
              <div className="active-delivery-card__loc-item">
                <h4>
                  <MapPin size={14} /> Customer Destination
                </h4>
                <p>{activeDelivery.customer_name}</p>
                <span>{activeDelivery.delivery_address}</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <span style={{ fontSize: '0.85rem', color: '#6B7280' }}>Payable Total: </span>
                <strong style={{ fontSize: '1.1rem', color: '#1F2937' }}>${activeDelivery.total_amount}</strong>
                <span className="badge badge--info" style={{ marginLeft: '0.5rem' }}>
                  {activeDelivery.payment_method}
                </span>
              </div>
              <Link to="/delivery/active-delivery">
                <Button variant="primary" size="md" icon={ArrowRight}>
                  Manage Delivery Run
                </Button>
              </Link>
            </div>
          </div>
        ) : (
          <div
            style={{
              background: '#FFFFFF',
              border: '1px solid #E5E7EB',
              borderRadius: '12px',
              padding: '2rem',
              textAlign: 'center',
              marginBottom: '2rem',
            }}
          >
            <div
              style={{
                width: '54px',
                height: '54px',
                borderRadius: '50%',
                background: '#ECFDF5',
                color: '#10B981',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem',
              }}
            >
              <Bike size={28} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.35rem' }}>
              You have no active deliveries right now
            </h3>
            <p style={{ color: '#6B7280', fontSize: '0.925rem', maxWidth: '440px', margin: '0 auto 1.25rem' }}>
              Check the available run requests below and claim an order to begin a delivery.
            </p>
            <Link to="/delivery/available-orders">
              <Button variant="secondary" size="md" icon={Navigation}>
                Browse Available Requests
              </Button>
            </Link>
          </div>
        )}

        {/* Available Requests Section */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#1F2937' }}>
              Available Delivery Runs
            </h3>
            <Link to="/delivery/available-orders" style={{ color: '#EA580C', fontWeight: 700, fontSize: '0.9rem', textDecoration: 'none' }}>
              View All ({stats.available_requests_count}) &rarr;
            </Link>
          </div>

          {availableOrders.length === 0 ? (
            <div style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '2rem', textAlign: 'center' }}>
              <p style={{ color: '#6B7280' }}>
                {stats.availability_status === 'AVAILABLE'
                  ? 'No ready orders right now. New requests will appear once kitchens mark food ready.'
                  : 'You are currently OFFLINE. Set status to AVAILABLE above to view available delivery runs.'}
              </p>
            </div>
          ) : (
            <div className="available-orders-grid">
              {availableOrders.map((ord) => (
                <div key={ord.order_id} className="available-order-card">
                  <div>
                    <div className="available-order-card__top">
                      <div>
                        <h4 className="available-order-card__rest-name">{ord.restaurant_name}</h4>
                        <p className="available-order-card__rest-addr">
                          <MapPin size={12} /> {ord.restaurant_address}
                        </p>
                      </div>
                      <span className="badge badge--success">Ready</span>
                    </div>

                    <div className="available-order-card__summary">
                      <div className="items-title">
                        <Package size={14} /> {ord.item_count} items to {ord.delivery_area}
                      </div>
                      <p>{ord.items_summary}</p>
                    </div>
                  </div>

                  <div className="available-order-card__footer">
                    <span className="available-order-card__price">${ord.total_amount}</span>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleClaimOrder(ord.order_id)}
                      disabled={stats.active_delivery_count > 0}
                    >
                      Accept Run
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
