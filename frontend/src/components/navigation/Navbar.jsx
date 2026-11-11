import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  UtensilsCrossed,
  Menu,
  X,
  ArrowRight,
  LogOut,
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
          <Link to="/restaurants" className="navbar__link">
            Browse Outlets
          </Link>

          {isAuthenticated ? (
            <>
              <Link to={dashboardPath} className="navbar__link">
                Dashboard
              </Link>
              {user?.role === 'RESTAURANT_OWNER' && (
                <>
                  <Link to="/restaurant/menu" className="navbar__link">
                    Menu Catalog
                  </Link>
                  <Link to="/restaurant/profile" className="navbar__link">
                    Outlet Profile
                  </Link>
                </>
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
          <Link
            to="/restaurants"
            className="navbar__mobile-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Browse Outlets
          </Link>

          {isAuthenticated ? (
            <>
              <div style={{ padding: '0.5rem 0', borderBottom: '1px solid #E5E7EB', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', color: '#6B7280' }}>
                  Signed in as <strong>{user?.full_name}</strong> ({user?.role})
                </span>
              </div>
              <Link
                to={dashboardPath}
                className="navbar__mobile-link"
                onClick={() => setMobileMenuOpen(false)}
              >
                My Dashboard
              </Link>
              {user?.role === 'RESTAURANT_OWNER' && (
                <>
                  <Link
                    to="/restaurant/menu"
                    className="navbar__mobile-link"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Menu Management
                  </Link>
                  <Link
                    to="/restaurant/profile"
                    className="navbar__mobile-link"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Restaurant Profile
                  </Link>
                </>
              )}
              <button
                type="button"
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="navbar__mobile-link"
                style={{ textAlign: 'left', background: 'none', border: 'none', color: '#EF4444' }}
              >
                Sign Out
              </button>
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
                href="/#how-it-works"
                className="navbar__mobile-link"
                onClick={() => setMobileMenuOpen(false)}
              >
                How It Works
              </a>
              <Link
                to="/login"
                className="navbar__mobile-link"
                onClick={() => setMobileMenuOpen(false)}
              >
                Sign In
              </Link>
              <Link
                to="/register/customer"
                className="navbar__mobile-link"
                onClick={() => setMobileMenuOpen(false)}
              >
                Register as Student
              </Link>
              <Link
                to="/register/restaurant-owner"
                className="navbar__mobile-link"
                onClick={() => setMobileMenuOpen(false)}
              >
                Register as Restaurant
              </Link>
            </>
          )}
        </div>
      )}
    </header>
  );
}
