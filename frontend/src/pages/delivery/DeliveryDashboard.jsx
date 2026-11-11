import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Bike, Navigation, DollarSign, Activity } from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

export default function DeliveryDashboard() {
  const { user } = useAuth();
  const courier = user?.delivery_profile;

  return (
    <div className="container" style={{ padding: '3rem 1rem' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span className="badge badge--success">Student Courier Portal</span>
          <span className="badge badge--primary">Active Fleet</span>
        </div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#1F2937' }}>
          Welcome, {user?.full_name || 'Courier'}!
        </h1>
        <p style={{ color: '#4B5563', fontSize: '1rem' }}>
          Courier Profile: {user?.email} | Mode: {courier?.vehicle_type || 'BICYCLE'}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#ECFDF5', color: '#10B981', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bike size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Vehicle Mode</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>{courier?.vehicle_type || 'Bicycle'}</h3>
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#FFEDD5', color: '#F97316', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Activity size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Dispatch Status</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#10B981' }}>On-Duty & Ready</h3>
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#EFF6FF', color: '#3B82F6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <DollarSign size={22} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>Daily Earnings</p>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1F2937' }}>$0.00 (Ready)</h3>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: '#ECFDF5', color: '#10B981', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
            <Navigation size={32} />
          </div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#1F2937', marginBottom: '0.5rem' }}>
            Campus Run Dispatch
          </h2>
          <p style={{ color: '#6B7280', maxWidth: '440px', margin: '0 auto 1.5rem', fontSize: '0.925rem' }}>
            You are authenticated as a Delivery Partner. Live order pickups, smart hall routing, and PIN delivery confirmations will be unlocked in Phase 4.
          </p>
          <Button variant="secondary" size="md" icon={Bike} onClick={() => alert('Delivery dispatch queue will be unlocked in Phase 4.')}>
            View Dispatch Queue
          </Button>
        </div>
      </Card>
    </div>
  );
}
