import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Utensils, ShoppingBag, Clock, MapPin, UserCheck } from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

export default function CustomerDashboard() {
  const { user } = useAuth();

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
          Browse food outlets, track active deliveries, and manage your campus meal orders.
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
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#ECFDF5', color: '#10B981', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Clock size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Average Delivery</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>&lt; 20 Mins</h3>
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#EFF6FF', color: '#3B82F6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <MapPin size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Dorm Deliveries</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>Campus-Wide Active</h3>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: '#FFEDD5', color: '#F97316', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
            <ShoppingBag size={32} />
          </div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.5rem' }}>
            Ready for your next meal?
          </h2>
          <p style={{ color: '#6B7280', maxWidth: '440px', margin: '0 auto 1.5rem', fontSize: '0.925rem' }}>
            Browse menus from dining halls, cafes, and campus eateries. Order workflows and checkout will be unlocked in Phase 4.
          </p>
          <a href="/#roles">
            <Button variant="primary" size="md" icon={Utensils}>
              Explore Campus Outlets
            </Button>
          </a>
        </div>
      </Card>
    </div>
  );
}
