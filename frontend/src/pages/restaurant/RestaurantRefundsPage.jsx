import React, { useState, useEffect } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  XCircle,
  HelpCircle,
  RefreshCw,
  DollarSign,
  ShieldAlert,
} from 'lucide-react';
import refundService from '../../services/refundService';
import Button from '../../components/common/Button';
import './RestaurantRefunds.scss';

export default function RestaurantRefundsPage() {
  const [refunds, setRefunds] = useState([]);
  const [total, setTotal] = useState(0);
  const [activeTab, setActiveTab] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');

  // Modal states
  const [selectedRefund, setSelectedRefund] = useState(null);
  const [modalType, setModalType] = useState(null); // 'APPROVE' | 'REJECT' | 'RESOLVE'
  const [approvedAmount, setApprovedAmount] = useState('');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchRefunds = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const params = {
        page: 1,
        size: 50,
      };
      if (activeTab !== 'ALL') {
        params.status = activeTab;
      }
      const data = await refundService.getRestaurantRefunds(params);
      setRefunds(data.requests || []);
      setTotal(data.total || 0);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to load restaurant refund requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRefunds();
  }, [activeTab]);

  const handleUnderReview = async (refundId) => {
    try {
      await refundService.markUnderReview(refundId);
      setActionSuccess('Request marked as Under Review.');
      fetchRefunds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Action failed.');
    }
  };

  const openApproveModal = (refund) => {
    setSelectedRefund(refund);
    setApprovedAmount(refund.requested_amount);
    setResolutionNotes('Refund approved for item issue.');
    setModalType('APPROVE');
  };

  const openRejectModal = (refund) => {
    setSelectedRefund(refund);
    setRejectionReason('');
    setModalType('REJECT');
  };

  const openResolveModal = (refund) => {
    setSelectedRefund(refund);
    setResolutionNotes('Settled via payment gateway reversal.');
    setModalType('RESOLVE');
  };

  const closeModal = () => {
    setSelectedRefund(null);
    setModalType(null);
    setApprovedAmount('');
    setResolutionNotes('');
    setRejectionReason('');
  };

  const submitApprove = async (e) => {
    e.preventDefault();
    if (!selectedRefund) return;
    setIsSubmitting(true);
    try {
      await refundService.approveRefund(selectedRefund.id, {
        approved_amount: parseFloat(approvedAmount),
        resolution_notes: resolutionNotes,
      });
      setActionSuccess('Refund approved successfully.');
      closeModal();
      fetchRefunds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to approve refund.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitReject = async (e) => {
    e.preventDefault();
    if (!selectedRefund) return;
    if (!rejectionReason.trim()) {
      alert('A reason is required to reject the refund.');
      return;
    }
    setIsSubmitting(true);
    try {
      await refundService.rejectRefund(selectedRefund.id, {
        explanation: rejectionReason.trim(),
      });
      setActionSuccess('Refund request rejected.');
      closeModal();
      fetchRefunds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to reject refund.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitResolve = async (e) => {
    e.preventDefault();
    if (!selectedRefund) return;
    setIsSubmitting(true);
    try {
      await refundService.resolveRefund(selectedRefund.id, {
        resolution_notes: resolutionNotes,
      });
      setActionSuccess('Refund marked as Resolved.');
      closeModal();
      fetchRefunds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to resolve refund.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const categoryLabels = {
    MISSING_ITEM: 'Missing Item(s)',
    INCORRECT_ITEM: 'Incorrect Item(s)',
    DAMAGED_FOOD: 'Damaged / Spilled Food',
    POOR_QUALITY: 'Poor Food Quality',
    OTHER: 'Other Issue',
  };

  return (
    <div className="restaurant-refunds-page">
      <div className="container">
        {/* Header */}
        <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1>Refund & Issue Management</h1>
            <p>Review customer claims, verify issues, and approve or reject settlements</p>
          </div>
          <button
            type="button"
            onClick={fetchRefunds}
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

        {actionSuccess && (
          <div style={{ background: '#ECFDF5', color: '#065F46', padding: '1rem', borderRadius: '0.75rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{actionSuccess}</span>
            <button onClick={() => setActionSuccess('')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}>✕</button>
          </div>
        )}

        {/* Status Tabs */}
        <div className="tabs-bar">
          {['ALL', 'PENDING', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'RESOLVED'].map((tab) => (
            <button
              key={tab}
              type="button"
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.replace('_', ' ')}
            </button>
          ))}
        </div>

        {/* Content */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <p style={{ color: '#64748b' }}>Loading refund claims...</p>
          </div>
        ) : errorMsg ? (
          <div style={{ background: '#FEF2F2', color: '#991B1B', padding: '2rem', textAlign: 'center', borderRadius: '1rem' }}>
            <AlertCircle size={32} style={{ marginBottom: '0.5rem' }} />
            <p>{errorMsg}</p>
          </div>
        ) : refunds.length === 0 ? (
          <div style={{ background: '#FFFFFF', border: '1px dashed #CBD5E1', borderRadius: '1rem', padding: '4rem 2rem', textAlign: 'center' }}>
            <ShieldAlert size={48} color="#94A3B8" style={{ marginBottom: '1rem' }} />
            <h3>No Refund Requests Found</h3>
            <p style={{ color: '#64748B' }}>
              {activeTab === 'ALL'
                ? 'Your kitchen has zero pending refund disputes.'
                : `No refund claims with status ${activeTab.replace('_', ' ')}.`}
            </p>
          </div>
        ) : (
          <div className="refunds-list">
            {refunds.map((refund) => (
              <div key={refund.id} className="refund-card">
                <div className="card-top">
                  <div className="info-left">
                    <h3>Order #{refund.order_id.substring(0, 8).toUpperCase()}</h3>
                    <div className="meta-line">
                      <span>Customer: <strong>{refund.customer_name || 'Campus Student'}</strong></span>
                      <span>•</span>
                      <span>{new Date(refund.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                  <span className={`status-pill ${refund.status.toLowerCase()}`}>
                    {refund.status.replace('_', ' ')}
                  </span>
                </div>

                <div className="card-details">
                  <span className="category-tag">
                    {categoryLabels[refund.issue_category] || refund.issue_category}
                  </span>
                  <p className="description-text">"{refund.description}"</p>
                  <div className="amounts-row">
                    <div>
                      <span>Requested: </span>
                      <strong>₹{parseFloat(refund.requested_amount).toFixed(2)}</strong>
                    </div>
                    {refund.approved_amount && (
                      <div>
                        <span>Approved: </span>
                        <strong style={{ color: '#059669' }}>
                          ₹{parseFloat(refund.approved_amount).toFixed(2)}
                        </strong>
                      </div>
                    )}
                  </div>
                </div>

                {refund.owner_response && (
                  <div className="owner-feedback">
                    <strong>Kitchen Explanation:</strong> {refund.owner_response}
                  </div>
                )}

                {refund.resolution_notes && (
                  <div className="owner-feedback" style={{ background: '#F0FDF4', borderColor: '#22C55E', color: '#166534' }}>
                    <strong>Resolution Notes:</strong> {refund.resolution_notes}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="card-actions">
                  {refund.status === 'PENDING' && (
                    <>
                      <Button
                        variant="outline"
                        size="small"
                        icon={Clock}
                        onClick={() => handleUnderReview(refund.id)}
                      >
                        Investigate (Under Review)
                      </Button>
                      <Button
                        variant="secondary"
                        size="small"
                        icon={CheckCircle2}
                        onClick={() => openApproveModal(refund)}
                      >
                        Approve Refund
                      </Button>
                      <Button
                        variant="danger"
                        size="small"
                        icon={XCircle}
                        onClick={() => openRejectModal(refund)}
                      >
                        Reject Claim
                      </Button>
                    </>
                  )}

                  {refund.status === 'UNDER_REVIEW' && (
                    <>
                      <Button
                        variant="secondary"
                        size="small"
                        icon={CheckCircle2}
                        onClick={() => openApproveModal(refund)}
                      >
                        Approve Refund
                      </Button>
                      <Button
                        variant="danger"
                        size="small"
                        icon={XCircle}
                        onClick={() => openRejectModal(refund)}
                      >
                        Reject Claim
                      </Button>
                    </>
                  )}

                  {refund.status === 'APPROVED' && (
                    <Button
                      variant="primary"
                      size="small"
                      icon={CheckCircle2}
                      onClick={() => openResolveModal(refund)}
                    >
                      Mark as Resolved / Settled
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal: Approve */}
        {modalType === 'APPROVE' && selectedRefund && (
          <div className="modal-overlay">
            <div className="modal-box">
              <h3>Approve Refund</h3>
              <p>
                Authorize settlement for order #{selectedRefund.order_id.substring(0, 8).toUpperCase()}.
              </p>
              <form onSubmit={submitApprove}>
                <div className="form-group">
                  <label>Approved Amount (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    max={selectedRefund.requested_amount}
                    value={approvedAmount}
                    onChange={(e) => setApprovedAmount(e.target.value)}
                    required
                  />
                  <small style={{ color: '#64748B' }}>
                    Max allowed: ₹{parseFloat(selectedRefund.requested_amount).toFixed(2)}
                  </small>
                </div>
                <div className="form-group">
                  <label>Resolution Notes / Kitchen Message</label>
                  <textarea
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    placeholder="Provide context or apology for the student..."
                  />
                </div>
                <div className="modal-actions">
                  <Button variant="outline" type="button" onClick={closeModal}>
                    Cancel
                  </Button>
                  <Button variant="primary" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Approving...' : 'Confirm Approval'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Reject */}
        {modalType === 'REJECT' && selectedRefund && (
          <div className="modal-overlay">
            <div className="modal-box">
              <h3>Reject Refund Request</h3>
              <p>
                Please specify a clear explanation for rejecting order #{selectedRefund.order_id.substring(0, 8).toUpperCase()}.
              </p>
              <form onSubmit={submitReject}>
                <div className="form-group">
                  <label>Mandatory Explanation / Reason</label>
                  <textarea
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="e.g. Courier photographic proof shows complete package was delivered intact..."
                    required
                  />
                </div>
                <div className="modal-actions">
                  <Button variant="outline" type="button" onClick={closeModal}>
                    Cancel
                  </Button>
                  <Button variant="danger" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Rejecting...' : 'Confirm Rejection'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Resolve */}
        {modalType === 'RESOLVE' && selectedRefund && (
          <div className="modal-overlay">
            <div className="modal-box">
              <h3>Resolve & Close Refund</h3>
              <p>
                Confirm that settlement has been processed for order #{selectedRefund.order_id.substring(0, 8).toUpperCase()}.
              </p>
              <form onSubmit={submitResolve}>
                <div className="form-group">
                  <label>Settlement Confirmation / Notes</label>
                  <textarea
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    placeholder="e.g. Gateway transaction reference or student cash reversal confirmation..."
                  />
                </div>
                <div className="modal-actions">
                  <Button variant="outline" type="button" onClick={closeModal}>
                    Cancel
                  </Button>
                  <Button variant="primary" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Processing...' : 'Mark Resolved'}
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

