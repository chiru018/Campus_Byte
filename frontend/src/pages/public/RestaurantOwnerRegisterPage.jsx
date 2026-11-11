import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Store, AlertCircle, CheckCircle2, UserPlus } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Button from '../../components/common/Button';
import './Auth.scss';

export default function RestaurantOwnerRegisterPage() {
  const { registerRestaurantOwner, login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
    confirm_password: '',
    restaurant_name: '',
    restaurant_address: '',
    restaurant_description: '',
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
      await registerRestaurantOwner({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone_number: form.phone_number.trim(),
        password: form.password,
        confirm_password: form.confirm_password,
        restaurant_name: form.restaurant_name.trim(),
        restaurant_address: form.restaurant_address.trim(),
        restaurant_description: form.restaurant_description.trim() || undefined,
      });

      setSuccessMsg('Restaurant partner profile created! Logging in...');
      await login(form.email.trim(), form.password);
      setTimeout(() => {
        navigate('/restaurant/dashboard', { replace: true });
      }, 1000);
    } catch (err) {
      setErrorMsg(err.message || 'Restaurant owner registration failed.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card auth-card--wide">
        <div className="auth-card__header">
          <div className="auth-card__badge-icon">
            <Store size={24} />
          </div>
          <h2 className="auth-card__title">Restaurant Partner Onboarding</h2>
          <p className="auth-card__subtitle">
            Connect your dining establishment to hundreds of campus students
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
          <div className="auth-card__row">
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="owner-name">
                Owner Full Name *
              </label>
              <input
                id="owner-name"
                name="full_name"
                type="text"
                className="auth-card__input"
                placeholder="Chef Mario"
                value={form.full_name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="owner-email">
                Contact Email *
              </label>
              <input
                id="owner-email"
                name="email"
                type="email"
                className="auth-card__input"
                placeholder="mario@restaurant.com"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="auth-card__row">
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="rest-name">
                Restaurant Name *
              </label>
              <input
                id="rest-name"
                name="restaurant_name"
                type="text"
                className="auth-card__input"
                placeholder="Campus Trattoria"
                value={form.restaurant_name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="owner-phone">
                Phone Number *
              </label>
              <input
                id="owner-phone"
                name="phone_number"
                type="tel"
                className="auth-card__input"
                placeholder="+1 (555) 000-5555"
                value={form.phone_number}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="rest-addr">
              Campus Outlet Location / Address *
            </label>
            <input
              id="rest-addr"
              name="restaurant_address"
              type="text"
              className="auth-card__input"
              placeholder="Student Center, 1st Floor Food Court"
              value={form.restaurant_address}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="rest-desc">
              Cuisine Description (Optional)
            </label>
            <input
              id="rest-desc"
              name="restaurant_description"
              type="text"
              className="auth-card__input"
              placeholder="Fresh Italian pizza, calzones, pasta, and salads"
              value={form.restaurant_description}
              onChange={handleChange}
            />
          </div>

          <div className="auth-card__row">
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="owner-pass">
                Password *
              </label>
              <input
                id="owner-pass"
                name="password"
                type="password"
                className="auth-card__input"
                placeholder="Min 8 characters"
                value={form.password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="owner-confirm">
                Confirm Password *
              </label>
              <input
                id="owner-confirm"
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
            {loading ? 'Creating Partner Profile...' : 'Register Restaurant'}
          </Button>
        </form>

        <div className="auth-card__footer">
          <p>
            Already an onboarded partner? <Link to="/login">Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

