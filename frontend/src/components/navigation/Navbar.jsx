import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  UtensilsCrossed,
  Menu,
  X,
  ArrowRight,
  LogOut,
  User as UserIcon,
  Store,
  Bike,
  LayoutDashboard,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Button from '../common/Button';
import './Navbar.scss';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, logout, getRoleDashboard } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/', { replace: true });
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'RESTAURANT_OWNER':
        return Store;
      case 'DELIVERY_PARTNER':
        return Bike;
      default:
        return LayoutDashboard;
    }
  };

  const dashboardPath = user ? getRoleDashboard(user.role) : '/';
  const RoleIcon = user ? getRoleIcon(user.role) : LayoutDashboard;

  return (
    <header className="navbar">
      <div className="container navbar__container">
        <Link to="/" className="navbar__brand">
          <div className="navbar__logo-badge">
            <UtensilsCrossed size={22} className="navbar__logo-icon" />
          </div>
          <div className="navbar__logo-text">
            <span>Campus</span>
            <span className="navbar__logo-highlight">Byte</span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="navbar__links">
          {isAuthenticated ? (
            <>
              <Link to={dashboardPath} className="navbar__link">
                Dashboard
              </Link>
              {user?.role === 'CUSTOMER' && (
                <a href="/#roles" className="navbar__link">Browse Outlets</a>
              )}
              {user?.role === 'RESTAURANT_OWNER' && (
                <span className="navbar__link" style={{ opacity: 0.8 }}>Kitchen Station</span>
              )}
              {user?.role === 'DELIVERY_PARTNER' && (
                <span className="navbar__link" style={{ opacity: 0.8 }}>Campus Fleet</span>
              )}
            </>
          ) : (
            <>
              <a href="/#roles" className="navbar__link">Who We Serve</a>
              <a href="/#how-it-works" className="navbar__link">How It Works</a>
              <a href="/#tech-stack" className="navbar__link">Platform</a>
            </>
          )}
        </nav>

        {/* Desktop Action Buttons */}
        <div className="navbar__actions">
          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Link to={dashboardPath}>
                <Button variant="secondary" size="sm" icon={RoleIcon}>
                  {user?.full_name?.split(' ')[0] || 'My Account'} ({user?.role?.split('_')[0]})
                </Button>
              </Link>
              <Button
                variant="ghost"
                size="sm"
                icon={LogOut}
                onClick={handleLogout}
              >
                Sign Out
              </Button>
            </div>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link to="/register/customer">
                <Button variant="primary" size="sm" icon={ArrowRight}>
                  Get Started
                </Button>
              </Link>
            </>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <button
          className="navbar__toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="navbar__mobile-menu">
          {isAuthenticated ? (
            <>
              <div style={{ padding: '0.5rem 0', borderBottom: '1px solid #E5E7EB', marginBottom: '0.5rem' }}>
                <p style={{ fontWeight: 700, color: '#1F2937' }}>{user?.full_name}</p>
                <p style={{ fontSize: '0.75rem', color: '#6B7280' }}>{user?.email} ({user?.role})</p>
              </div>
              <Link
                to={dashboardPath}
                className="navbar__mobile-link"
                onClick={() => setMobileMenuOpen(false)}
              >
                My Role Dashboard
              </Link>
              <div className="navbar__mobile-actions">
                <Button
                  variant="secondary"
                  size="md"
                  className="btn--full"
                  icon={LogOut}
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                >
                  Sign Out
                </Button>
              </div>
            </>
          ) : (
            <>
              <a
                href="/#roles"
                className="navbar__mobile-link"
                onClick={() => setMobileMenuOpen(false)}
              >
                Who We Serve
              </a>
              <a
                href="/#tech-stack"
                className="navbar__mobile-link"
                onClick={() => setMobileMenuOpen(false)}
              >
                Platform
              </a>
              <div className="navbar__mobile-actions">
                <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="secondary" size="md" className="btn--full">
                    Sign In
                  </Button>
                </Link>
                <Link to="/register/customer" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="primary" size="md" className="btn--full">
                    Register as Customer
                  </Button>
                </Link>
                <Link to="/register/restaurant-owner" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="ghost" size="sm" className="btn--full">
                    Register as Restaurant Owner
                  </Button>
                </Link>
                <Link to="/register/delivery-partner" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="ghost" size="sm" className="btn--full">
                    Register as Courier
                  </Button>
                </Link>
              </div>
            </>
          )}
        </div>
      )}
    </header>
  );
}
