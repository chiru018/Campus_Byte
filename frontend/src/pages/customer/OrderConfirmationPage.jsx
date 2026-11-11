import React, { useState, useEffect } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import {
  CheckCircle,
  Package,
  MapPin,
  Clock,
  ArrowRight,
  Store,
  Banknote,
} from 'lucide-react';
import orderService from '../../services/orderService';
import Button from '../../components/common/Button';
import './Orders.scss';

export default function OrderConfirmationPage() {
  const { orderId } = useParams();
  const location = useLocation();

  const [order, setOrder] = useState(location.state?.order || null);
  const [loading, setLoading] = useState(!location.state?.order);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!order && orderId) {
      const fetchOrder = async () => {
        try {
          const data = await orderService.getOrderById(orderId);
          setOrder(data);
        } catch (err) {
          setErrorMsg(err.response?.data?.detail || 'Unable to load order details.');
        } finally {
          setLoading(false);
        }
      };
      fetchOrder();
    }
  }, [orderId, order]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '6rem 0', minHeight: '60vh' }}>
        <p>Loading your order confirmation...</p>
      </div>
    );
  }

  if (errorMsg || !order) {
    return (
      <div className="orders-page">
        <div className="container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <h2>Order Not Found</h2>
          <p style={{ color: '#64748B', marginBottom: '2rem' }}>
            {errorMsg || 'We could not locate this order confirmation.'}
          </p>
          <Link to="/restaurants">
            <Button variant="primary">Browse Restaurants</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="orders-page">
      <div className="container">
        <div className="order-confirmation-card">
          {/* Success Graphic */}
          <div className="success-badge">
            <CheckCircle size={44} color="#10B981" />
          </div>

          <h1>Order Placed Successfully!</h1>
          <p className="subtitle">
            Thank you for ordering with Campus Byte. The restaurant has received your order and will begin preparing it shortly.
          </p>

          <div className="order-meta-box">
            <div className="meta-item">
              <span className="meta-label">Order Number</span>
              <span className="meta-val">#{order.id.substring(0, 8).toUpperCase()}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Restaurant</span>
              <span className="meta-val">{order.restaurant_name || 'Campus Food Outlet'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Total to Pay (COD)</span>
              <span className="meta-val highlight">${parseFloat(order.total_amount).toFixed(2)}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Status</span>
              <span className="status-pill pending">Order Placed</span>
            </div>
          </div>

          {/* Details breakdown */}
          <div className="confirmation-details">
            <div className="detail-section">
              <h3>
                <MapPin size={18} color="#F59E0B" /> Delivery Address
              </h3>
              <p>{order.delivery_address}</p>
            </div>

            <div className="detail-section">
              <h3>
                <Banknote size={18} color="#10B981" /> Payment Option
              </h3>
              <p>Cash on Delivery (Please have exact cash ready for the courier)</p>
            </div>

            <div className="detail-section">
              <h3>
                <Package size={18} color="#3B82F6" /> Items Ordered ({order.order_items?.length || 0})
              </h3>
              <div className="items-mini-list">
                {order.order_items?.map((item) => (
                  <div key={item.id} className="item-mini-row">
                    <span>
                      {item.quantity}x {item.item_name}
                    </span>
                    <span>${parseFloat(item.total_price).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Navigation Action Buttons */}
          <div className="confirmation-actions">
            <Link to={`/my-orders/${order.id}`}>
              <Button variant="primary" icon={Clock}>
                Track Order Status
              </Button>
            </Link>
            <Link to="/restaurants">
              <Button variant="secondary" icon={Store}>
                Browse More Outlets
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
