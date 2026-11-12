import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ShoppingBag,
  ArrowRight,
  Store,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import orderService from '../../services/orderService';
import Button from '../../components/common/Button';
import './Orders.scss';

export default function MyOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filterTab, setFilterTab] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const fetchOrders = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      // Map tab filter to backend status query or filter client-side for multi-status tabs
      let statusQuery = null;
      if (filterTab === 'DELIVERED') statusQuery = 'DELIVERED';
      if (filterTab === 'CANCELLED') statusQuery = 'CANCELLED';

      const data = await orderService.getMyOrders({
        page,
        size: 30,
        status: statusQuery,
      });

      let items = data.orders || [];
      if (filterTab === 'ACTIVE') {
        items = items.filter((o) =>
          ['PENDING', 'ACCEPTED', 'PREPARING', 'READY_FOR_PICKUP', 'PICKED_UP', 'OUT_FOR_DELIVERY'].includes(
            o.order_status
          )
        );
      }

      setOrders(items);
      setTotal(data.total || 0);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to retrieve your order history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [page, filterTab]);

  const getStatusBadge = (status) => {
    const s = (status || '').toLowerCase();
    const displayLabels = {
      pending: 'Order Placed',
      accepted: 'Accepted',
      preparing: 'Preparing Food',
      ready_for_pickup: 'Ready for Pickup',
      picked_up: 'Courier Picked Up',
      out_for_delivery: 'Out For Delivery',
      delivered: 'Delivered',
      cancelled: 'Cancelled',
      rejected: 'Rejected',
    };

    return (
      <span className={`status-pill ${s}`}>
        {displayLabels[s] || status}
      </span>
    );
  };

  return (
    <div className="orders-page">
      <div className="container">
        {/* Header */}
        <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1>My Order History</h1>
            <p>Track live deliveries and view your previous food orders</p>
          </div>
          <button
            type="button"
            onClick={fetchOrders}
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
            <RefreshCw size={15} /> Refresh
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="orders-filter-tabs">
          <button
            type="button"
            className={filterTab === 'ALL' ? 'active' : ''}
            onClick={() => setFilterTab('ALL')}
          >
            All Orders
          </button>
          <button
            type="button"
            className={filterTab === 'ACTIVE' ? 'active' : ''}
            onClick={() => setFilterTab('ACTIVE')}
          >
            Active Orders
          </button>
          <button
            type="button"
            className={filterTab === 'DELIVERED' ? 'active' : ''}
            onClick={() => setFilterTab('DELIVERED')}
          >
            Completed
          </button>
          <button
            type="button"
            className={filterTab === 'CANCELLED' ? 'active' : ''}
            onClick={() => setFilterTab('CANCELLED')}
          >
            Cancelled
          </button>
        </div>

        {/* Orders Content */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <p style={{ color: '#64748B' }}>Loading your orders...</p>
          </div>
        ) : errorMsg ? (
          <div
            style={{
              padding: '2rem',
              textAlign: 'center',
              background: '#FEF2F2',
              borderRadius: '1rem',
              color: '#991B1B',
            }}
          >
            <AlertCircle size={32} style={{ marginBottom: '0.5rem' }} />
            <p>{errorMsg}</p>
          </div>
        ) : orders.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              background: '#FFFFFF',
              borderRadius: '1rem',
              border: '1px dashed #CBD5E1',
              padding: '4rem 1.5rem',
              maxWidth: '520px',
              margin: '2rem auto',
            }}
          >
            <ShoppingBag size={48} color="#94A3B8" style={{ marginBottom: '1rem' }} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0F172A', marginBottom: '0.5rem' }}>
              No Orders Found
            </h2>
            <p style={{ color: '#64748B', fontSize: '0.925rem', marginBottom: '1.5rem' }}>
              {filterTab === 'ALL'
                ? "You haven't placed any food orders yet. Ready for a delicious meal?"
                : `You don't have any ${filterTab.toLowerCase()} orders.`}
            </p>
            <Link to="/restaurants">
              <Button variant="primary" icon={ArrowRight}>
                Explore Campus Outlets
              </Button>
            </Link>
          </div>
        ) : (
          <div className="orders-list">
            {orders.map((order) => {
              const formattedDate = new Date(order.created_at).toLocaleString([], {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              });

              // Construct readable items summary
              const itemsSummary =
                order.order_items?.length > 0
                  ? order.order_items
                      .map((i) => `${i.quantity}x ${i.item_name}`)
                      .join(', ')
                  : 'Food items';

              return (
                <div key={order.id} className="order-history-card">
                  <div className="card-top">
                    <div className="restaurant-info">
                      <h3>{order.restaurant_name || 'Campus Restaurant'}</h3>
                      <span className="order-date">{formattedDate}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      {getStatusBadge(order.order_status)}
                      <span className="order-id-tag">
                        #{order.id.substring(0, 8).toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className="card-middle">
                    <div className="items-summary">
                      <strong>Items:</strong> {itemsSummary}
                    </div>

                    <div className="price-summary">
                      <span className="price-label">Total Amount</span>
                      <span className="price-val">
                        ${parseFloat(order.total_amount).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <div className="card-bottom">
                    <div style={{ fontSize: '0.85rem', color: '#64748B' }}>
                      <strong>Delivery to:</strong> {order.delivery_address}
                    </div>

                    <Link to={`/my-orders/${order.id}`}>
                      <Button variant="outline" size="small" icon={Clock}>
                        Track & Details
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

