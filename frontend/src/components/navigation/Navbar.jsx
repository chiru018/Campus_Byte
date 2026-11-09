import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { UtensilsCrossed, Menu, X, ArrowRight } from 'lucide-react';
import Button from '../common/Button';
import './Navbar.scss';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
          <a href="#roles" className="navbar__link">Who We Serve</a>
          <a href="#how-it-works" className="navbar__link">How It Works</a>
          <a href="#tech-stack" className="navbar__link">Platform</a>
        </nav>

        {/* Desktop Action Buttons */}
        <div className="navbar__actions">
          <Link to="/login">
            <Button variant="ghost" size="sm">
              Sign In
            </Button>
          </Link>
          <Link to="/register">
            <Button variant="primary" size="sm" icon={ArrowRight}>
              Get Started
            </Button>
          </Link>
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
          <a
            href="#roles"
            className="navbar__mobile-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Who We Serve
          </a>
          <a
            href="#how-it-works"
            className="navbar__mobile-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            How It Works
          </a>
          <a
            href="#tech-stack"
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
            <Link to="/register" onClick={() => setMobileMenuOpen(false)}>
              <Button variant="primary" size="md" className="btn--full">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
