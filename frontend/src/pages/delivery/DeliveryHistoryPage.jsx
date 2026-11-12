import React, { useState, useEffect } from 'react';
import {
  History,
  CheckCircle2,
  MapPin,
  Clock,
  DollarSign,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import deliveryService from '../../services/deliveryService';
import DeliverySidebar from '../../components/navigation/DeliverySidebar';
import Button from '../../components/common/Button';
import './Delivery.scss';

export default function DeliveryHistoryPage() {
  const { user } = useAuth();
  const [historyItems, setHistoryItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [stats, setStats] = useState({ availability_status: 'AVAILABLE', active_delivery_count: 0 });
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const fetchHistory = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const [histData, profData, statsData] = await Promise.all([
        deliveryService.getDeliveryHistory({
          status: statusFilter === 'ALL' ? undefined : statusFilter,
          page,
          size: 20,
        }),
        deliveryService.getProfile(),
        deliveryService.getDashboardStatistics(),
      ]);
      setHistoryItems(histData.items || []);
      setTotal(histData.total || 0);
      setProfile(profData);
      setStats(statsData);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to load delivery history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, statusFilter]);

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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1F2937' }}>
              Delivery History
            </h1>
            <p style={{ color: '#6B7280', fontSize: '0.95rem' }}>
              Historical archive of completed and fulfilled campus food delivery runs
            </p>
          </div>
          <Button variant="secondary" size="sm" icon={RefreshCw} onClick={fetchHistory} disabled={loading}>
            Refresh
          </Button>
        </div>

        {errorMsg && (
          <div className="auth-card__alert auth-card__alert--error" style={{ marginBottom: '1.5rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Filter Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          {['ALL', 'DELIVERED', 'CANCELLED'].map((st) => (
            <button
              key={st}
              onClick={() => {
                setStatusFilter(st);
                setPage(1);
              }}
              className={`button button--sm ${statusFilter === st ? 'button--primary' : 'button--outline'}`}
            >
              {st === 'ALL' ? 'All Deliveries' : st === 'DELIVERED' ? 'Completed' : 'Cancelled'}
            </button>
          ))}
        </div>

        {historyItems.length === 0 ? (
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
              <History size={28} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.35rem' }}>
              No delivery records found
            </h3>
            <p style={{ color: '#6B7280', fontSize: '0.925rem', maxWidth: '420px', margin: '0 auto' }}>
              Completed delivery runs and verified COD handovers will be automatically recorded here.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {historyItems.map((item) => (
              <div
                key={item.assignment_id}
                style={{
                  background: '#FFFFFF',
                  border: '1px solid #E5E7EB',
                  borderRadius: '12px',
                  padding: '1.25rem 1.5rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '1rem',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                    <span style={{ fontWeight: 800, color: '#1F2937', fontSize: '1.05rem' }}>
                      Order #{item.order_id.slice(0, 8)}
                    </span>
                    <span className={`badge ${item.delivery_status === 'DELIVERED' ? 'badge--success' : 'badge--secondary'}`}>
                      {item.delivery_status}
                    </span>
                    {item.cod_collected && (
                      <span className="badge badge--primary">COD Paid</span>
                    )}
                  </div>
                  <p style={{ color: '#4B5563', fontSize: '0.9rem', marginBottom: '0.2rem' }}>
                    <strong>{item.restaurant_name}</strong> &rarr; {item.delivery_address}
                  </p>
                  <p style={{ color: '#9CA3AF', fontSize: '0.785rem' }}>
                    <Clock size={12} style={{ display: 'inline', marginRight: '4px' }} />
                    Assigned: {new Date(item.assigned_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                    {item.completed_at && ` | Completed: ${new Date(item.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
                  </p>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1F2937' }}>
                    ${item.total_amount}
                  </div>
                  <span style={{ fontSize: '0.8rem', color: '#6B7280' }}>
                    {item.payment_method}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
