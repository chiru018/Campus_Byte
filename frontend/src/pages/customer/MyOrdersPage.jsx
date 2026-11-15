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
  Star,
  ShieldAlert,
  Edit2,
  Trash2,
} from 'lucide-react';
import orderService from '../../services/orderService';
import reviewService from '../../services/reviewService';
import refundService from '../../services/refundService';
import StarRating from '../../components/StarRating';
import Button from '../../components/common/Button';
import './Orders.scss';

export default function MyOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [refunds, setRefunds] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filterTab, setFilterTab] = useState('ALL'); // 'ALL' | 'ACTIVE' | 'DELIVERED' | 'CANCELLED' | 'REVIEWS' | 'REFUNDS'
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Modals
  const [reviewModalOrder, setReviewModalOrder] = useState(null);
  const [editingReview, setEditingReview] = useState(null);
  const [rating, setRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');

  const [refundModalOrder, setRefundModalOrder] = useState(null);
  const [refundCategory, setRefundCategory] = useState('MISSING_ITEM');
  const [refundDescription, setRefundDescription] = useState('');
  const [requestedAmount, setRequestedAmount] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchOrders = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      if (filterTab === 'REVIEWS') {
        const myReviews = await reviewService.getMyReviews();
        setReviews(myReviews || []);
      } else if (filterTab === 'REFUNDS') {
        const myRefunds = await refundService.getMyRefundRequests();
        setRefunds(myRefunds.requests || []);
      } else {
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
      }
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to retrieve your order history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [page, filterTab]);

  const openReviewModal = (order) => {
    setReviewModalOrder(order);
    setEditingReview(null);
    setRating(5);
    setReviewComment('');
  };

  const openEditReviewModal = (review) => {
    setEditingReview(review);
    setReviewModalOrder(null);
    setRating(review.rating);
    setReviewComment(review.comment || '');
  };

  const closeReviewModal = () => {
    setReviewModalOrder(null);
    setEditingReview(null);
    setRating(5);
    setReviewComment('');
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (editingReview) {
        await reviewService.updateReview(editingReview.id, {
          rating,
          comment: reviewComment,
        });
        setSuccessMsg('Review updated successfully!');
      } else if (reviewModalOrder) {
        await reviewService.submitReview({
          order_id: reviewModalOrder.id,
          restaurant_id: reviewModalOrder.restaurant_id,
          rating,
          comment: reviewComment,
        });
        setSuccessMsg('Thank you for rating your campus meal!');
      }
      closeReviewModal();
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit review.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm('Are you sure you want to delete this review?')) return;
    try {
      await reviewService.deleteReview(reviewId);
      setSuccessMsg('Review deleted.');
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete review.');
    }
  };

  const openRefundModal = (order) => {
    setRefundModalOrder(order);
    setRefundCategory('MISSING_ITEM');
    setRefundDescription('');
    setRequestedAmount(parseFloat(order.total_amount).toFixed(2));
  };

  const closeRefundModal = () => {
    setRefundModalOrder(null);
    setRefundDescription('');
    setRequestedAmount('');
  };

  const handleRefundSubmit = async (e) => {
    e.preventDefault();
    if (!refundModalOrder) return;
    const reqAmount = parseFloat(requestedAmount);
    const maxAmount = parseFloat(refundModalOrder.total_amount);

    if (isNaN(reqAmount) || reqAmount <= 0) {
      alert('Please enter a valid requested refund amount.');
      return;
    }
    if (reqAmount > maxAmount) {
      alert(`Requested amount cannot exceed order total of ₹${maxAmount.toFixed(2)}.`);
      return;
    }
    if (refundDescription.trim().length < 10) {
      alert('Please provide a detailed explanation of the issue (at least 10 characters).');
      return;
    }

    setIsSubmitting(true);
    try {
      await refundService.createRefundRequest({
        order_id: refundModalOrder.id,
        issue_category: refundCategory,
        description: refundDescription.trim(),
        requested_amount: reqAmount,
      });
      setSuccessMsg('Refund request submitted to kitchen for review.');
      closeRefundModal();
      fetchOrders();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit refund request.');
    } finally {
      setIsSubmitting(false);
    }
  };

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
            <p>Track live deliveries, rate meals, and submit refund requests</p>
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

        {successMsg && (
          <div style={{ background: '#ECFDF5', color: '#065F46', padding: '1rem', borderRadius: '0.75rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{successMsg}</span>
            <button onClick={() => setSuccessMsg('')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}>✕</button>
          </div>
        )}

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
          <button
            type="button"
            className={filterTab === 'REVIEWS' ? 'active' : ''}
            onClick={() => setFilterTab('REVIEWS')}
          >
            ⭐ My Reviews
          </button>
          <button
            type="button"
            className={filterTab === 'REFUNDS' ? 'active' : ''}
            onClick={() => setFilterTab('REFUNDS')}
          >
            🛡️ Refund Requests
          </button>
        </div>

        {/* Orders Content */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <p style={{ color: '#64748B' }}>Loading data...</p>
          </div>
        ) : errorMsg ? (
          <div style={{ padding: '2rem', textAlign: 'center', background: '#FEF2F2', borderRadius: '1rem', color: '#991B1B' }}>
            <AlertCircle size={32} style={{ marginBottom: '0.5rem' }} />
            <p>{errorMsg}</p>
          </div>
        ) : filterTab === 'REVIEWS' ? (
          /* My Reviews Tab */
          <div>
            {reviews.length === 0 ? (
              <div style={{ textAlign: 'center', background: '#FFFFFF', borderRadius: '1rem', border: '1px dashed #CBD5E1', padding: '3.5rem 1.5rem', maxWidth: '520px', margin: '2rem auto' }}>
                <Star size={44} color="#F59E0B" style={{ marginBottom: '1rem' }} />
                <h3>No Reviews Submitted Yet</h3>
                <p style={{ color: '#64748B', fontSize: '0.925rem' }}>
                  Completed meal deliveries can be reviewed to share your experience with campus diners!
                </p>
              </div>
            ) : (
              reviews.map((r) => (
                <div key={r.id} className="review-item-card">
                  <div className="item-header">
                    <div>
                      <h4>{r.restaurant_name || 'Campus Outlet'}</h4>
                      <span className="item-date">{new Date(r.created_at).toLocaleDateString()}</span>
                    </div>
                    <StarRating rating={r.rating} readonly size="sm" showValue />
                  </div>
                  <p className="item-body">"{r.comment || 'No comment provided.'}"</p>
                  <div className="item-footer">
                    <span>Order #{r.order_id.substring(0, 8).toUpperCase()}</span>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        type="button"
                        onClick={() => openEditReviewModal(r)}
                        style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', background: '#F1F5F9', border: 'none', padding: '0.35rem 0.65rem', borderRadius: '0.35rem', cursor: 'pointer', fontSize: '0.8rem' }}
                      >
                        <Edit2 size={13} /> Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteReview(r.id)}
                        style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', background: '#FEF2F2', color: '#DC2626', border: 'none', padding: '0.35rem 0.65rem', borderRadius: '0.35rem', cursor: 'pointer', fontSize: '0.8rem' }}
                      >
                        <Trash2 size={13} /> Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : filterTab === 'REFUNDS' ? (
          /* My Refund Requests Tab */
          <div>
            {refunds.length === 0 ? (
              <div style={{ textAlign: 'center', background: '#FFFFFF', borderRadius: '1rem', border: '1px dashed #CBD5E1', padding: '3.5rem 1.5rem', maxWidth: '520px', margin: '2rem auto' }}>
                <ShieldAlert size={44} color="#94A3B8" style={{ marginBottom: '1rem' }} />
                <h3>No Refund Claims Filed</h3>
                <p style={{ color: '#64748B', fontSize: '0.925rem' }}>
                  If you have an issue with a delivered order, you can report it from the Completed orders tab.
                </p>
              </div>
            ) : (
              refunds.map((ref) => (
                <div key={ref.id} className="refund-item-card">
                  <div className="item-header">
                    <div>
                      <h4>Order #{ref.order_id.substring(0, 8).toUpperCase()}</h4>
                      <span className="item-date">{new Date(ref.created_at).toLocaleString()}</span>
                    </div>
                    <span className={`status-pill ${ref.status.toLowerCase()}`}>
                      {ref.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div style={{ margin: '0.4rem 0', fontSize: '0.85rem' }}>
                    <strong>Category:</strong> {ref.issue_category.replace('_', ' ')}
                  </div>
                  <p className="item-body">"{ref.description}"</p>
                  <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    <span>Requested: <strong>₹{parseFloat(ref.requested_amount).toFixed(2)}</strong></span>
                    {ref.approved_amount && (
                      <span style={{ color: '#059669' }}>
                        Approved: <strong>₹{parseFloat(ref.approved_amount).toFixed(2)}</strong>
                      </span>
                    )}
                  </div>
                  {ref.owner_response && (
                    <div style={{ background: '#EFF6FF', padding: '0.5rem 0.75rem', borderRadius: '0.35rem', fontSize: '0.825rem', color: '#1E3A8A' }}>
                      <strong>Kitchen response:</strong> {ref.owner_response}
                    </div>
                  )}
                  {ref.resolution_notes && (
                    <div style={{ background: '#F0FDF4', padding: '0.5rem 0.75rem', borderRadius: '0.35rem', fontSize: '0.825rem', color: '#166534', marginTop: '0.35rem' }}>
                      <strong>Resolution:</strong> {ref.resolution_notes}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        ) : orders.length === 0 ? (
          <div style={{ textAlign: 'center', background: '#FFFFFF', borderRadius: '1rem', border: '1px dashed #CBD5E1', padding: '4rem 1.5rem', maxWidth: '520px', margin: '2rem auto' }}>
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

              const itemsSummary =
                order.order_items?.length > 0
                  ? order.order_items
                      .map((i) => `${i.quantity}x ${i.item_name}`)
                      .join(', ')
                  : 'Food items';

              const isDelivered = order.order_status === 'DELIVERED';

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
                        ₹{parseFloat(order.total_amount).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <div className="card-bottom">
                    <div style={{ fontSize: '0.85rem', color: '#64748B' }}>
                      <strong>Delivery to:</strong> {order.delivery_address}
                    </div>

                    <div className="order-action-btns">
                      {isDelivered && (
                        <>
                          <Button
                            variant="secondary"
                            size="small"
                            icon={Star}
                            onClick={() => openReviewModal(order)}
                          >
                            Review Meal
                          </Button>
                          <Button
                            variant="outline"
                            size="small"
                            icon={ShieldAlert}
                            onClick={() => openRefundModal(order)}
                          >
                            Report Issue
                          </Button>
                        </>
                      )}

                      <Link to={`/my-orders/${order.id}`}>
                        <Button variant="outline" size="small" icon={Clock}>
                          Track & Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Modal: Review Meal */}
        {(reviewModalOrder || editingReview) && (
          <div className="order-modal-overlay">
            <div className="order-modal-box">
              <h3>{editingReview ? 'Edit Your Review' : 'Rate & Review Your Meal'}</h3>
              <p className="modal-subtitle">
                {editingReview
                  ? 'Update your rating and comment'
                  : `Share your thoughts about your meal from ${reviewModalOrder?.restaurant_name || 'the kitchen'}`}
              </p>

              <form onSubmit={handleReviewSubmit}>
                <div className="form-group" style={{ textAlign: 'center', padding: '1rem 0' }}>
                  <label style={{ marginBottom: '0.75rem' }}>Your Rating</label>
                  <StarRating
                    rating={rating}
                    onChange={(val) => setRating(val)}
                    size="lg"
                    showValue
                  />
                </div>

                <div className="form-group">
                  <label>Review Comment (Optional)</label>
                  <textarea
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    placeholder="How was the food taste, packaging, and portion size?"
                    maxLength={1000}
                  />
                </div>

                <div className="modal-actions">
                  <Button variant="outline" type="button" onClick={closeReviewModal}>
                    Cancel
                  </Button>
                  <Button variant="primary" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Submitting...' : editingReview ? 'Save Changes' : 'Submit Review'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Report Issue / Refund */}
        {refundModalOrder && (
          <div className="order-modal-overlay">
            <div className="order-modal-box">
              <h3>Report Issue / Request Refund</h3>
              <p className="modal-subtitle">
                Order #{refundModalOrder.id.substring(0, 8).toUpperCase()} • Total: ₹{parseFloat(refundModalOrder.total_amount).toFixed(2)}
              </p>

              <form onSubmit={handleRefundSubmit}>
                <div className="form-group">
                  <label>Issue Category</label>
                  <select
                    value={refundCategory}
                    onChange={(e) => setRefundCategory(e.target.value)}
                    required
                  >
                    <option value="MISSING_ITEM">Missing Item(s)</option>
                    <option value="INCORRECT_ITEM">Incorrect Item(s)</option>
                    <option value="DAMAGED_FOOD">Damaged / Spilled Food</option>
                    <option value="POOR_QUALITY">Poor Quality / Spoiled</option>
                    <option value="OTHER">Other Issue</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Requested Refund Amount (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    max={refundModalOrder.total_amount}
                    value={requestedAmount}
                    onChange={(e) => setRequestedAmount(e.target.value)}
                    required
                  />
                  <small style={{ color: '#64748B' }}>
                    Maximum eligible refund: ₹{parseFloat(refundModalOrder.total_amount).toFixed(2)}
                  </small>
                </div>

                <div className="form-group">
                  <label>Detailed Explanation of Issue</label>
                  <textarea
                    value={refundDescription}
                    onChange={(e) => setRefundDescription(e.target.value)}
                    placeholder="Please specify exactly what went wrong (minimum 10 characters)..."
                    required
                    minLength={10}
                    maxLength={2000}
                  />
                </div>

                <div className="modal-actions">
                  <Button variant="outline" type="button" onClick={closeRefundModal}>
                    Cancel
                  </Button>
                  <Button variant="danger" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Submitting...' : 'Submit Claim'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
