import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  ClipboardList,
  Bell,
  Clock,
  CheckCircle,
  ChefHat,
  PackageCheck,
  XCircle,
  Search,
  RefreshCw,
  AlertTriangle,
  ArrowRight,
  Eye,
  Loader2,
  X,
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

export default function RestaurantOrdersPage() {
  const [restaurant, setRestaurant] = useState(null);
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState({
    total_orders: 0,
    pending_orders: 0,
    accepted_orders: 0,
    preparing_orders: 0,
    ready_for_pickup_orders: 0,
    rejected_orders: 0,
    cancelled_orders: 0,
    delivered_orders: 0,
  });

  const [activeTab, setActiveTab] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Notification Banner State
  const [newOrderAlert, setNewOrderAlert] = useState(null);
  const lastCursorRef = useRef(null);

  // Rejection Dialog Modal State
  const [rejectingOrder, setRejectingOrder] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [rejectionError, setRejectionError] = useState('');
  const [rejectSubmitting, setRejectSubmitting] = useState(false);

  // Fetch Restaurant Profile
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await restaurantService.getMyRestaurant();
        setRestaurant(data);
      } catch (err) {
        console.error('Failed to load restaurant profile:', err);
      }
    };
    fetchProfile();
  }, []);

  // Fetch Orders and Stats
  const loadData = async (isBackground = false) => {
    if (!isBackground) setLoading(true);
    try {
      let statusQuery = null;
      if (activeTab === 'PENDING') statusQuery = 'PENDING';
      else if (activeTab === 'ACCEPTED') statusQuery = 'ACCEPTED';
      else if (activeTab === 'PREPARING') statusQuery = 'PREPARING';
      else if (activeTab === 'READY_FOR_PICKUP') statusQuery = 'READY_FOR_PICKUP';

      const [ordersRes, statsRes] = await Promise.all([
        restaurantOrderService.getOrders({
          page,
          size: 25,
          status: statusQuery,
          search: searchTerm,
        }),
        restaurantOrderService.getOrderStats(),
      ]);

      let items = ordersRes.orders || [];
      if (activeTab === 'COMPLETED') {
        items = items.filter((o) =>
          ['DELIVERED', 'CANCELLED', 'REJECTED'].includes(o.order_status)
        );
      }

      setOrders(items);
      setTotal(ordersRes.total || 0);
      setStats(statsRes);
      setErrorMsg('');
    } catch (err) {
      if (!isBackground) {
        setErrorMsg(err.response?.data?.detail || 'Failed to retrieve orders.');
      }
    } finally {
      if (!isBackground) setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeTab, searchTerm, page]);

  // Polling for incoming orders notifications every 12 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const notif = await restaurantOrderService.getNotifications(lastCursorRef.current);
        if (notif.new_orders_count > 0 && notif.pending_orders.length > 0) {
          const newest = notif.pending_orders[0];
          setNewOrderAlert(newest);
          lastCursorRef.current = notif.latest_cursor;
          // Refresh background data
          loadData(true);
        }
      } catch (err) {
        // Silent failure on polling interval
      }
    }, 12000);

    return () => clearInterval(interval);
  }, [activeTab, searchTerm]);

  // ==========================================
  // ORDER ACTION HANDLERS
  // ==========================================

  const handleAccept = async (orderId) => {
    setActionLoadingId(orderId);
    try {
      await restaurantOrderService.acceptOrder(orderId);
      if (newOrderAlert?.id === orderId) {
        setNewOrderAlert(null);
      }
      loadData(true);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to accept order.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const openRejectModal = (order) => {
    setRejectingOrder(order);
    setRejectionReason('');
    setRejectionError('');
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
      await restaurantOrderService.rejectOrder(rejectingOrder.id, rejectionReason.trim());
      if (newOrderAlert?.id === rejectingOrder.id) {
        setNewOrderAlert(null);
      }
      setRejectingOrder(null);
      loadData(true);
    } catch (err) {
      setRejectionError(err.response?.data?.detail || 'Failed to reject order.');
    } finally {
      setRejectSubmitting(false);
    }
  };

  const handleStartPrep = async (orderId) => {
    setActionLoadingId(orderId);
    try {
      await restaurantOrderService.startPreparation(orderId);
      loadData(true);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to start food preparation.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleMarkReady = async (orderId) => {
    setActionLoadingId(orderId);
    try {
      await restaurantOrderService.markReadyForPickup(orderId);
      loadData(true);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to mark order ready for pickup.');
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <div className="restaurant-orders-page">
      <div className="container">
        <div className="dashboard-layout">
          {/* Sidebar */}
          <RestaurantSidebar
            restaurantName={restaurant?.name}
            isOpen={restaurant?.is_open}
            pendingCount={stats.pending_orders}
          />

          {/* Main Workspace */}
          <main className="dashboard-main">
            {/* Top Bar */}
            <div className="orders-header">
              <div className="header-text">
                <h1>Live Orders Management</h1>
                <p>Manage incoming orders, acknowledge kitchen tasks, and track meal preparation</p>
              </div>

              <div className="header-controls">
                <button
                  type="button"
                  onClick={() => loadData(false)}
                  disabled={loading}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    background: '#FFFFFF',
                    border: '1px solid #CBD5E1',
                    borderRadius: '0.5rem',
                    padding: '0.55rem 0.95rem',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    color: '#334155',
                    cursor: 'pointer',
                  }}
                >
                  <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
                  Refresh
                </button>
              </div>
            </div>

            {/* In-App New Incoming Order Alert Banner */}
            {newOrderAlert && (
              <div className="new-order-alert-banner">
                <div className="alert-content">
                  <div className="alert-icon-box">
                    <Bell size={24} />
                  </div>
                  <div>
                    <h3>New Incoming Order #{newOrderAlert.id.substring(0, 8).toUpperCase()}!</h3>
                    <p>
                      {newOrderAlert.customer_name || 'Student'} just ordered {newOrderAlert.order_items?.length || 1} item(s) • Total ${parseFloat(newOrderAlert.total_amount).toFixed(2)} (Cash on Delivery)
                    </p>
                  </div>
                </div>

                <div className="alert-actions">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleAccept(newOrderAlert.id)}
                    disabled={actionLoadingId === newOrderAlert.id}
                  >
                    Accept Immediately
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => openRejectModal(newOrderAlert)}
                  >
                    Reject
                  </Button>
                  <button
                    type="button"
                    onClick={() => setNewOrderAlert(null)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#92400E', padding: '0.25rem' }}
                    title="Dismiss alert"
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>
            )}

            {/* Metrics Overview Cards */}
            <div className="metrics-grid">
              <div
                className={`metric-card ${activeTab === 'PENDING' ? 'active' : ''}`}
                onClick={() => setActiveTab('PENDING')}
              >
                <div className="metric-top">
                  <span>New Orders</span>
                  <Clock size={16} className="metric-icon" />
                </div>
                <div className="metric-value pending">{stats.pending_orders}</div>
              </div>

              <div
                className={`metric-card ${activeTab === 'ACCEPTED' ? 'active' : ''}`}
                onClick={() => setActiveTab('ACCEPTED')}
              >
                <div className="metric-top">
                  <span>Accepted</span>
                  <CheckCircle size={16} className="metric-icon" />
                </div>
                <div className="metric-value accepted">{stats.accepted_orders}</div>
              </div>

              <div
                className={`metric-card ${activeTab === 'PREPARING' ? 'active' : ''}`}
                onClick={() => setActiveTab('PREPARING')}
              >
                <div className="metric-top">
                  <span>Preparing</span>
                  <ChefHat size={16} className="metric-icon" />
                </div>
                <div className="metric-value preparing">{stats.preparing_orders}</div>
              </div>

              <div
                className={`metric-card ${activeTab === 'READY_FOR_PICKUP' ? 'active' : ''}`}
                onClick={() => setActiveTab('READY_FOR_PICKUP')}
              >
                <div className="metric-top">
                  <span>Ready for Pickup</span>
                  <PackageCheck size={16} className="metric-icon" />
                </div>
                <div className="metric-value ready">{stats.ready_for_pickup_orders}</div>
              </div>

              <div
                className={`metric-card ${activeTab === 'ALL' ? 'active' : ''}`}
                onClick={() => setActiveTab('ALL')}
              >
                <div className="metric-top">
                  <span>Total Orders</span>
                  <ClipboardList size={16} className="metric-icon" />
                </div>
                <div className="metric-value">{stats.total_orders}</div>
              </div>
            </div>

            {/* Filter Tabs and Search Toolbar */}
            <div className="orders-toolbar">
              <div className="status-tabs">
                <button
                  type="button"
                  className={activeTab === 'ALL' ? 'active' : ''}
                  onClick={() => setActiveTab('ALL')}
                >
                  All Orders
                </button>
                <button
                  type="button"
                  className={activeTab === 'PENDING' ? 'active' : ''}
                  onClick={() => setActiveTab('PENDING')}
                >
                  New ({stats.pending_orders})
                </button>
                <button
                  type="button"
                  className={activeTab === 'ACCEPTED' ? 'active' : ''}
                  onClick={() => setActiveTab('ACCEPTED')}
                >
                  Accepted ({stats.accepted_orders})
                </button>
                <button
                  type="button"
                  className={activeTab === 'PREPARING' ? 'active' : ''}
                  onClick={() => setActiveTab('PREPARING')}
                >
                  Preparing ({stats.preparing_orders})
                </button>
                <button
                  type="button"
                  className={activeTab === 'READY_FOR_PICKUP' ? 'active' : ''}
                  onClick={() => setActiveTab('READY_FOR_PICKUP')}
                >
                  Ready for Pickup ({stats.ready_for_pickup_orders})
                </button>
                <button
                  type="button"
                  className={activeTab === 'COMPLETED' ? 'active' : ''}
                  onClick={() => setActiveTab('COMPLETED')}
                >
                  Completed / Other
                </button>
              </div>

              <div className="search-box">
                <Search size={16} className="search-icon" />
                <input
                  type="text"
                  placeholder="Search order ID, dorm, customer..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div
                style={{
                  padding: '1rem',
                  backgroundColor: '#FEF2F2',
                  border: '1px solid #FECACA',
                  borderRadius: '0.75rem',
                  color: '#991B1B',
                  marginBottom: '1.5rem',
                }}
              >
                {errorMsg}
              </div>
            )}

            {/* Orders Listing */}
            {loading ? (
              <div style={{ textAlign: 'center', padding: '4rem 0' }}>
                <Loader2 size={32} className="animate-spin" color="#F59E0B" style={{ margin: '0 auto 1rem' }} />
                <p style={{ color: '#64748B' }}>Loading restaurant orders...</p>
              </div>
            ) : orders.length === 0 ? (
              <div className="empty-orders-state">
                <div className="icon-box">
                  <ClipboardList size={32} />
                </div>
                <h3>No orders found</h3>
                <p>
                  {searchTerm
                    ? `No orders match your search "${searchTerm}".`
                    : activeTab === 'ALL'
                    ? 'No orders have been placed for your restaurant yet.'
                    : `No orders are currently in ${activeTab.replace('_', ' ').toLowerCase()} status.`}
                </p>
              </div>
            ) : (
              <div className="orders-grid">
                {orders.map((order) => {
                  const statusClass = order.order_status.toLowerCase();
                  const isPending = order.order_status === 'PENDING';
                  const isAccepted = order.order_status === 'ACCEPTED';
                  const isPreparing = order.order_status === 'PREPARING';
                  const isReady = order.order_status === 'READY_FOR_PICKUP';

                  return (
                    <div
                      key={order.id}
                      className={`restaurant-order-card status-${statusClass}`}
                    >
                      <div className="card-header-bar">
                        <div className="order-id-group">
                          <span className="order-code">
                            #{order.id.substring(0, 8).toUpperCase()}
                          </span>
                          <span className="order-time">
                            {new Date(order.created_at).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                            })} • {new Date(order.created_at).toLocaleDateString([], {
                              month: 'short',
                              day: 'numeric',
                            })}
                          </span>
                        </div>

                        <span className={`status-pill ${statusClass}`}>
                          {order.order_status.replace(/_/g, ' ')}
                        </span>
                      </div>

                      <div className="card-body-content">
                        {/* Customer & Location */}
                        <div className="customer-block">
                          <h4>Customer & Delivery Location</h4>
                          <p>
                            <strong>{order.customer_name || 'Campus Student'}</strong>
                            {order.customer_phone ? ` (${order.customer_phone})` : ''}
                          </p>
                          <p className="delivery-addr">
                            📍 {order.delivery_address}
                          </p>
                        </div>

                        {/* Items Breakdown */}
                        <div className="items-block">
                          <h4>Ordered Items ({order.order_items?.length || 0})</h4>
                          <div className="items-mini-list">
                            {order.order_items?.map((item) => (
                              <div key={item.id} className="item-row">
                                <span className="item-qty-name">
                                  {item.quantity}x {item.item_name}
                                </span>
                                <span className="item-subtotal">
                                  ${parseFloat(item.total_price).toFixed(2)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="card-actions-bar">
                        <div className="order-total-block">
                          <span className="label">Order Total Amount</span>
                          <div className="amount">
                            ${parseFloat(order.total_amount).toFixed(2)}
                            <span className="payment-badge">Cash on Delivery</span>
                          </div>
                        </div>

                        <div className="action-buttons">
                          {/* Inspect Details Link */}
                          <Link to={`/restaurant/orders/${order.id}`}>
                            <Button variant="outline" size="sm" icon={Eye}>
                              Details
                            </Button>
                          </Link>

                          {/* Action depending on state */}
                          {isPending && (
                            <>
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={() => handleAccept(order.id)}
                                disabled={actionLoadingId === order.id}
                              >
                                {actionLoadingId === order.id ? 'Accepting...' : 'Accept Order'}
                              </Button>
                              <Button
                                variant="danger"
                                size="sm"
                                onClick={() => openRejectModal(order)}
                                disabled={actionLoadingId === order.id}
                              >
                                Reject
                              </Button>
                            </>
                          )}

                          {isAccepted && (
                            <Button
                              variant="primary"
                              size="sm"
                              icon={ChefHat}
                              onClick={() => handleStartPrep(order.id)}
                              disabled={actionLoadingId === order.id}
                            >
                              {actionLoadingId === order.id ? 'Starting...' : 'Start Cooking'}
                            </Button>
                          )}

                          {isPreparing && (
                            <Button
                              variant="primary"
                              size="sm"
                              icon={PackageCheck}
                              style={{ backgroundColor: '#10B981', borderColor: '#10B981' }}
                              onClick={() => handleMarkReady(order.id)}
                              disabled={actionLoadingId === order.id}
                            >
                              {actionLoadingId === order.id ? 'Updating...' : 'Mark Ready for Pickup'}
                            </Button>
                          )}

                          {isReady && (
                            <span
                              style={{
                                fontSize: '0.85rem',
                                color: '#047857',
                                backgroundColor: '#D1FAE5',
                                padding: '0.4rem 0.8rem',
                                borderRadius: '0.5rem',
                                fontWeight: '700',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.35rem',
                              }}
                            >
                              <PackageCheck size={16} /> Awaiting Courier Pickup
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </main>
        </div>
      </div>

      {/* Reject Order Modal */}
      {rejectingOrder && (
        <div className="modal-overlay">
          <div className="rejection-modal">
            <div className="modal-header">
              <AlertTriangle size={24} />
              <h3>Reject Order #{rejectingOrder.id.substring(0, 8).toUpperCase()}</h3>
            </div>
            <p>
              Please state why the kitchen cannot fulfill this order. The customer will see this message.
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
                onClick={() => setRejectingOrder(null)}
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
