import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bike, AlertCircle, CheckCircle2, UserPlus } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Button from '../../components/common/Button';
import './Auth.scss';

export default function DeliveryPartnerRegisterPage() {
  const { registerDeliveryPartner, login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
    confirm_password: '',
    vehicle_type: 'BICYCLE',
    vehicle_registration_number: '',
  });
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (form.password !== form.confirm_password) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await registerDeliveryPartner({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone_number: form.phone_number.trim(),
        password: form.password,
        confirm_password: form.confirm_password,
        vehicle_type: form.vehicle_type,
        vehicle_registration_number: form.vehicle_registration_number.trim() || undefined,
      });

      setSuccessMsg('Courier account registered! Logging you in...');
      await login(form.email.trim(), form.password);
      setTimeout(() => {
        navigate('/delivery/dashboard', { replace: true });
      }, 1000);
    } catch (err) {
      setErrorMsg(err.message || 'Delivery partner registration failed.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-card__header">
          <div className="auth-card__badge-icon">
            <Bike size={24} />
          </div>
          <h2 className="auth-card__title">Join Campus Courier Fleet</h2>
          <p className="auth-card__subtitle">
            Earn on your schedule between lectures with zero vehicle hassles
          </p>
        </div>

        {errorMsg && (
          <div className="auth-card__alert auth-card__alert--error">
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="auth-card__alert auth-card__alert--success">
            <CheckCircle2 size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-card__form">
          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="courier-name">
              Full Name *
            </label>
            <input
              id="courier-name"
              name="full_name"
              type="text"
              className="auth-card__input"
              placeholder="Sam Rider"
              value={form.full_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="courier-email">
              Campus Email *
            </label>
            <input
              id="courier-email"
              name="email"
              type="email"
              className="auth-card__input"
              placeholder="sam@campus.edu"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-card__row">
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="courier-phone">
                Mobile Number *
              </label>
              <input
                id="courier-phone"
                name="phone_number"
                type="tel"
                className="auth-card__input"
                placeholder="+1 (555) 000-8888"
                value={form.phone_number}
                onChange={handleChange}
                required
              />
            </div>
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="courier-vehicle">
                Vehicle Type *
              </label>
              <select
                id="courier-vehicle"
                name="vehicle_type"
                className="auth-card__select"
                value={form.vehicle_type}
                onChange={handleChange}
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
          </div>

          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="courier-reg">
              Vehicle Registration / Campus Tag Number
            </label>
            <input
              id="courier-reg"
              name="vehicle_registration_number"
              type="text"
              className="auth-card__input"
              placeholder="e.g. CAMPUS-BIKE-102 (Optional)"
              value={form.vehicle_registration_number}
              onChange={handleChange}
            />
          </div>

          <div className="auth-card__row">
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="courier-pass">
                Password *
              </label>
              <input
                id="courier-pass"
                name="password"
                type="password"
                className="auth-card__input"
                placeholder="Min 8 chars"
                value={form.password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="courier-confirm">
                Confirm Password *
              </label>
              <input
                id="courier-confirm"
                name="confirm_password"
                type="password"
                className="auth-card__input"
                placeholder="Repeat password"
                value={form.confirm_password}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            icon={UserPlus}
            disabled={loading}
            style={{ width: '100%', marginTop: '0.5rem' }}
          >
            {loading ? 'Creating Courier Account...' : 'Register as Courier'}
          </Button>
        </form>

        <div className="auth-card__footer">
          <p>
            Already an active courier? <Link to="/login">Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

