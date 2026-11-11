import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Lock, Mail, Eye, EyeOff, AlertCircle, ArrowRight, LogIn } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Button from '../../components/common/Button';
import './Auth.scss';

export default function LoginPage() {
  const { login, isAuthenticated, user, getRoleDashboard } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // If already logged in, redirect to appropriate role dashboard
  const fromPath = location.state?.from?.pathname;
  React.useEffect(() => {
    if (isAuthenticated && user) {
      const destination = fromPath || getRoleDashboard(user.role);
      navigate(destination, { replace: true });
    }
  }, [isAuthenticated, user, navigate, fromPath, getRoleDashboard]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!email.trim() || !password) {
      setErrorMsg('Please enter both your email and password.');
      return;
    }

    setLoading(true);
    try {
      const loggedUser = await login(email.trim(), password);
      const destination = fromPath || getRoleDashboard(loggedUser.role);
      navigate(destination, { replace: true });
    } catch (err) {
      setErrorMsg(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-card__header">
          <div className="auth-card__badge-icon">
            <Lock size={24} />
          </div>
          <h2 className="auth-card__title">Sign In to Campus Byte</h2>
          <p className="auth-card__subtitle">
            Enter your credentials to access your campus dashboard
          </p>
        </div>

        {errorMsg && (
          <div className="auth-card__alert auth-card__alert--error">
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-card__form">
          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="login-email">
              Email Address
            </label>
            <div className="auth-card__input-wrapper">
              <input
                id="login-email"
                type="email"
                className="auth-card__input"
                placeholder="student@campus.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
          </div>

          <div className="auth-card__field">
            <label className="auth-card__label" htmlFor="login-password">
              Password
            </label>
            <div className="auth-card__input-wrapper">
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                className="auth-card__input auth-card__input--has-icon-right"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
              <button
                type="button"
                className="auth-card__icon-btn"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            icon={LogIn}
            disabled={loading}
            style={{ width: '100%', marginTop: '0.5rem' }}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </Button>
        </form>

        <div className="auth-card__footer">
          <p style={{ marginBottom: '0.75rem' }}>Don't have an account yet?</p>
          <div className="auth-card__role-options">
            <Link to="/register/customer">Register as Student Customer</Link>
            <Link to="/register/restaurant-owner">Partner as Restaurant Owner</Link>
            <Link to="/register/delivery-partner">Join as Student Courier</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
