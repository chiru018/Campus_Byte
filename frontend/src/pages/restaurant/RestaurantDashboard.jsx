import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Store, UtensilsCrossed, CheckCircle2, TrendingUp, Settings } from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

export default function RestaurantDashboard() {
  const { user } = useAuth();
  const restaurant = user?.restaurant;

  return (
    <div className="container" style={{ padding: '3rem 1rem' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span className="badge badge--secondary">Restaurant Owner Portal</span>
          <span className="badge badge--success">Kitchen Active</span>
        </div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#1F2937' }}>
          {restaurant?.name || 'Restaurant Management Hub'}
        </h1>
        <p style={{ color: '#4B5563', fontSize: '1rem' }}>
          Manager: {user?.full_name} ({user?.email})
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#FFEDD5', color: '#F97316', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Store size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Outlet Location</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>{restaurant?.address || 'Campus Location'}</h3>
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#ECFDF5', color: '#10B981', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CheckCircle2 size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Availability State</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#10B981' }}>Taking Orders (Open)</h3>
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#EFF6FF', color: '#3B82F6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <TrendingUp size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Order Dispatch</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>Live Station Ready</h3>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: '#F3F4F6', color: '#1F2937', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
            <UtensilsCrossed size={32} />
          </div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.5rem' }}>
            Menu & Station Management
          </h2>
          <p style={{ color: '#6B7280', maxWidth: '440px', margin: '0 auto 1.5rem', fontSize: '0.925rem' }}>
            You are authorized as a Restaurant Owner. Kitchen order queue and menu editor views will be enabled in subsequent phases.
          </p>
          <Button variant="secondary" size="md" icon={Settings} onClick={() => alert('Menu management workflows will be unlocked in Phase 4.')}>
            Configure Kitchen Menu
          </Button>
        </div>
      </Card>
    </div>
  );
}
