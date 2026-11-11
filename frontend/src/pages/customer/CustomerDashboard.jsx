import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import {
  Utensils,
  ShoppingBag,
  Clock,
  MapPin,
  UserCheck,
  ArrowRight,
  Package,
} from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

export default function CustomerDashboard() {
  const { user } = useAuth();
  const { totalItems, totalAmount } = useCart();

  return (
    <div className="container" style={{ padding: '3rem 1rem' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span className="badge badge--primary">Customer Portal</span>
          <span className="badge badge--success">Authenticated</span>
        </div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#1F2937' }}>
          Welcome back, {user?.full_name || 'Student'}!
        </h1>
        <p style={{ color: '#4B5563', fontSize: '1rem' }}>
          Order meals directly to your room, track live deliveries, and view your order history.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#FFEDD5', color: '#F97316', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <UserCheck size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Account Email</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>{user?.email}</h3>
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#FEF3C7', color: '#D97706', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShoppingBag size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Current Cart</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>
                {totalItems > 0 ? `${totalItems} items ($${totalAmount.toFixed(2)})` : 'Empty Cart'}
              </h3>
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#EFF6FF', color: '#3B82F6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <MapPin size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Delivery Coverage</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>All Campus Hostels</h3>
            </div>
          </div>
        </Card>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <Card>
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem' }}>
            <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: '#FFEDD5', color: '#F97316', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
              <Utensils size={32} />
            </div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.5rem' }}>
              Order Fresh Campus Meals
            </h2>
            <p style={{ color: '#6B7280', maxWidth: '400px', margin: '0 auto 1.5rem', fontSize: '0.925rem' }}>
              Browse dining halls, cafes, and campus food outlets. Add dishes to your cart and checkout with Cash on Delivery.
            </p>
            <Link to="/restaurants" style={{ textDecoration: 'none' }}>
              <Button variant="primary" size="md" icon={ArrowRight}>
                Browse Outlets & Menus
              </Button>
            </Link>
          </div>
        </Card>

        <Card>
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem' }}>
            <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: '#E0E7FF', color: '#4F46E5', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
              <Package size={32} />
            </div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.5rem' }}>
              Track Past & Active Orders
            </h2>
            <p style={{ color: '#6B7280', maxWidth: '400px', margin: '0 auto 1.5rem', fontSize: '0.925rem' }}>
              Check live status updates for in-progress deliveries, review your receipt breakdown, and manage cancellations.
            </p>
            <Link to="/my-orders" style={{ textDecoration: 'none' }}>
              <Button variant="outline" size="md" icon={Clock}>
                View My Order History
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
