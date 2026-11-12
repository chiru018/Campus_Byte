import React, { useState, useEffect } from 'react';
import {
  User,
  Bike,
  Phone,
  Mail,
  Shield,
  CheckCircle2,
  AlertCircle,
  Save,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import deliveryService from '../../services/deliveryService';
import DeliverySidebar from '../../components/navigation/DeliverySidebar';
import Button from '../../components/common/Button';
import './Delivery.scss';

export default function DeliveryProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState({ availability_status: 'AVAILABLE', active_delivery_count: 0 });
  const [form, setForm] = useState({
    vehicle_type: 'BICYCLE',
    vehicle_registration_number: '',
    phone_number: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const fetchProfile = async () => {
    try {
      const [profData, statsData] = await Promise.all([
        deliveryService.getProfile(),
        deliveryService.getDashboardStatistics(),
      ]);
      setProfile(profData);
      setStats(statsData);
      setForm({
        vehicle_type: profData.vehicle_type || 'BICYCLE',
        vehicle_registration_number: profData.vehicle_registration_number || '',
        phone_number: profData.phone_number || '',
      });
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to load profile.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const updated = await deliveryService.updateProfile({
        vehicle_type: form.vehicle_type,
        vehicle_registration_number: form.vehicle_registration_number.trim() || undefined,
        phone_number: form.phone_number.trim() || undefined,
      });
      setProfile(updated);
      setSuccessMsg('Courier profile updated successfully.');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

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
        <div style={{ marginBottom: '1.5rem' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1F2937' }}>
            Courier Fleet Profile
          </h1>
          <p style={{ color: '#6B7280', fontSize: '0.95rem' }}>
            Configure your delivery vehicle mode, campus registration tag, and contact details
          </p>
        </div>

        {errorMsg && (
          <div className="auth-card__alert auth-card__alert--error" style={{ marginBottom: '1.5rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div className="auth-card__alert auth-card__alert--success" style={{ marginBottom: '1.5rem' }}>
            <CheckCircle2 size={18} />
            <span>{successMsg}</span>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {/* Account Overview Card */}
          <div style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#1F2937', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={20} color="#EA580C" /> Courier Credentials
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.785rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>
                  Full Legal Name
                </label>
                <p style={{ fontSize: '1rem', fontWeight: 600, color: '#1F2937', margin: '0.2rem 0 0' }}>
                  {user?.full_name}
                </p>
              </div>

              <div>
                <label style={{ fontSize: '0.785rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>
                  Campus Account Email
                </label>
                <p style={{ fontSize: '1rem', fontWeight: 600, color: '#1F2937', margin: '0.2rem 0 0' }}>
                  {user?.email}
                </p>
              </div>

              <div>
                <label style={{ fontSize: '0.785rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>
                  Fleet Role
                </label>
                <p style={{ fontSize: '0.95rem', fontWeight: 700, color: '#EA580C', margin: '0.2rem 0 0' }}>
                  DELIVERY_PARTNER (Verified)
                </p>
              </div>

              <div>
                <label style={{ fontSize: '0.785rem', textTransform: 'uppercase', color: '#6B7280', fontWeight: 700 }}>
                  Account Created
                </label>
                <p style={{ fontSize: '0.9rem', color: '#6B7280', margin: '0.2rem 0 0' }}>
                  {profile?.created_at ? new Date(profile.created_at).toLocaleDateString([], { dateStyle: 'long' }) : 'Active'}
                </p>
              </div>
            </div>
          </div>

          {/* Vehicle & Contact Form */}
          <div style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#1F2937', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Bike size={20} color="#EA580C" /> Vehicle & Contact Settings
            </h3>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#374151', marginBottom: '0.35rem' }}>
                  Active Vehicle Mode *
                </label>
                <select
                  className="auth-card__select"
                  value={form.vehicle_type}
                  onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}
                  required
                >
                  <option value="BICYCLE">Bicycle</option>
                  <option value="SCOOTER">Electric Scooter</option>
                  <option value="WALKING">Walking / On Foot</option>
                  <option value="MOTORCYCLE">Motorcycle</option>
                  <option value="BIKE">Bike</option>
                  <option value="CAR">Car</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#374151', marginBottom: '0.35rem' }}>
                  Vehicle Plate or Campus Registration Tag
                </label>
                <input
                  type="text"
                  className="auth-card__input"
                  placeholder="e.g. CAMPUS-BIKE-102"
                  value={form.vehicle_registration_number}
                  onChange={(e) => setForm({ ...form, vehicle_registration_number: e.target.value })}
                />
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#374151', marginBottom: '0.35rem' }}>
                  Mobile Dispatch Contact Number *
                </label>
                <input
                  type="tel"
                  className="auth-card__input"
                  placeholder="+1 (555) 000-8888"
                  value={form.phone_number}
                  onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
                  required
                />
              </div>

              <Button type="submit" variant="primary" size="md" icon={Save} disabled={saving}>
                {saving ? 'Saving Changes...' : 'Save Profile Changes'}
              </Button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}

