import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Utensils, AlertCircle, CheckCircle2, UserPlus } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Button from '../../components/common/Button';
import './Auth.scss';

export default function CustomerRegisterPage() {
  const { registerCustomer, login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
    confirm_password: '',
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
      await registerCustomer({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone_number: form.phone_number.trim() || undefined,
        password: form.password,
        confirm_password: form.confirm_password,
      });

      setSuccessMsg('Account created successfully! Logging you in...');
      // Automatic login after successful registration
      const user = await login(form.email.trim(), form.password);
      setTimeout(() => {
        navigate('/customer/dashboard', { replace: true });
      }, 1000);
    } catch (err) {
      setErrorMsg(err.message || 'Registration failed.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-card__header">
          <div className="auth-card__badge-icon">
            <Utensils size={24} />
          </div>
          <h2 className="auth-card__title">Customer Registration</h2>
          <p className="auth-card__subtitle">
            Order campus meals directly to your dorm or study hall
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
            <label className="auth-card__label" htmlFor="cust-name">
              Full Name *
            </label>
            <input
              id="cust-name"
              name="full_name"
              type="text"
              className="auth-card__input"
              placeholder="Alex Johnson"
              value={form.full_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="cust-email">
              Campus Email *
            </label>
            <input
              id="cust-email"
              name="email"
              type="email"
              className="auth-card__input"
              placeholder="alex@campus.edu"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="cust-phone">
              Phone Number (Optional)
            </label>
            <input
              id="cust-phone"
              name="phone_number"
              type="tel"
              className="auth-card__input"
              placeholder="+1 (555) 000-1234"
              value={form.phone_number}
              onChange={handleChange}
            />
          </div>

          <div className="auth-card__row">
            <div className="auth-card__field">
              <label className="auth-card__label" htmlFor="cust-pass">
                Password *
              </label>
              <input
                id="cust-pass"
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
              <label className="auth-card__label" htmlFor="cust-confirm">
                Confirm Password *
              </label>
              <input
                id="cust-confirm"
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

          <p style={{ fontSize: '0.75rem', color: '#6B7280' }}>
            Password must have 8+ characters, including uppercase, lowercase, number, and special character.
          </p>

          <Button
            type="submit"
            variant="primary"
            size="md"
            icon={UserPlus}
            disabled={loading}
            style={{ width: '100%', marginTop: '0.5rem' }}
          >
            {loading ? 'Creating Account...' : 'Register as Customer'}
          </Button>
        </form>

        <div className="auth-card__footer">
          <p>
            Already have an account? <Link to="/login">Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
