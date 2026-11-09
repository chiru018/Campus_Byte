import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Utensils,
  Store,
  Bike,
  ArrowRight,
  CheckCircle2,
  Clock,
  MapPin,
  ShieldAlert,
  Server,
  Activity,
  Sparkles,
} from 'lucide-react';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import { checkHealth, getApiRoot } from '../../services/api';
import './LandingPage.scss';

export default function LandingPage() {
  const [apiStatus, setApiStatus] = useState({
    loading: true,
    healthy: false,
    message: '',
    error: null,
  });

  useEffect(() => {
    let isMounted = true;
    async function verifyBackend() {
      try {
        const [rootData, healthData] = await Promise.all([
          getApiRoot(),
          checkHealth(),
        ]);
        if (isMounted) {
          setApiStatus({
            loading: false,
            healthy: healthData.status === 'healthy',
            message: rootData.message || 'Campus Byte API Online',
            error: null,
          });
        }
      } catch (err) {
        if (isMounted) {
          setApiStatus({
            loading: false,
            healthy: false,
            message: 'API Offline (Start backend server)',
            error: err.message,
          });
        }
      }
    }
    verifyBackend();
    return () => {
      isMounted = false;
    };
  }, []);

  const roles = [
    {
      id: 'customer',
      title: 'Hungry Students & Faculty',
      roleName: 'Customer',
      tagline: 'Fresh meals delivered right to your dorm, library, or quad.',
      icon: Utensils,
      badgeColor: 'primary',
      features: [
        'Explore campus canteens and local restaurants',
        'Real-time order progress & live delivery updates',
        'Student-friendly pricing and transparent fees',
      ],
      ctaText: 'Start Ordering',
      ctaLink: '/register?role=customer',
    },
    {
      id: 'restaurant',
      title: 'Campus Food Partners',
      roleName: 'Restaurant Owner',
      tagline: 'Boost your kitchen throughput and connect with campus demand.',
      icon: Store,
      badgeColor: 'secondary',
      features: [
        'Dynamic menu, pricing, and modifier control',
        'Instant order dispatch & prep station tracking',
        'Detailed sales metrics and peak-hour analytics',
      ],
      ctaText: 'Partner With Us',
      ctaLink: '/register?role=restaurant',
    },
    {
      id: 'delivery',
      title: 'Student Couriers',
      roleName: 'Delivery Partner',
      tagline: 'Earn on your schedule between lectures with zero vehicle hassles.',
      icon: Bike,
      badgeColor: 'success',
      features: [
        'Walk, cycle, or scoot between classes and dorms',
        'Instant payout calculations and daily earnings',
        'Smart campus routing optimized for building entrances',
      ],
      ctaText: 'Become a Courier',
      ctaLink: '/register?role=delivery',
    },
  ];

  return (
    <div className="landing">
      {/* Backend Status Bar */}
      <section className="landing__status-bar">
        <div className="container landing__status-container">
          <div className="landing__status-indicator">
            <span
              className={`status-dot ${
                apiStatus.loading
                  ? 'status-dot--loading'
                  : apiStatus.healthy
                  ? 'status-dot--online'
                  : 'status-dot--offline'
              }`}
            />
            <span className="status-label">
              <Server size={14} className="status-icon" />
              <strong>FastAPI Backend Status:</strong>
              {apiStatus.loading
                ? ' Checking connection...'
                : apiStatus.healthy
                ? ` ${apiStatus.message} (v1 healthy)`
                : ` ${apiStatus.message}`}
            </span>
          </div>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="landing__status-doc-link"
          >
            <Activity size={14} /> View Swagger Docs
          </a>
        </div>
      </section>

      {/* Hero Section */}
      <section className="hero">
        <div className="container hero__container">
          <div className="hero__content">
            <div className="badge badge--primary hero__badge">
              <Sparkles size={14} /> The All-in-One Campus Food Network
            </div>
            <h1 className="hero__title">
              Cravings Delivered to your <span className="text-highlight">Campus Spot</span>
            </h1>
            <p className="hero__description">
              Campus Byte links hungry students, campus dining spots, and student couriers
              into a unified, hyper-fast delivery ecosystem. Built for collegiate life.
            </p>

            <div className="hero__actions">
              <Link to="/register">
                <Button variant="primary" size="lg" icon={ArrowRight}>
                  Explore Menus
                </Button>
              </Link>
              <a href="#roles">
                <Button variant="secondary" size="lg">
                  Explore Roles
                </Button>
              </a>
            </div>

            <div className="hero__stats">
              <div className="hero__stat-item">
                <div className="hero__stat-icon">
                  <Clock size={18} />
                </div>
                <div>
                  <h4 className="hero__stat-number">&lt; 25 mins</h4>
                  <p className="hero__stat-label">Average campus drop</p>
                </div>
              </div>
              <div className="hero__stat-item">
                <div className="hero__stat-icon">
                  <MapPin size={18} />
                </div>
                <div>
                  <h4 className="hero__stat-number">100% Dorm</h4>
                  <p className="hero__stat-label">Door-to-door coverage</p>
                </div>
              </div>
            </div>
          </div>

          <div className="hero__visual">
            <div className="hero__card-stack">
              <div className="floating-card floating-card--top">
                <div className="floating-card__icon-badge floating-card__icon-badge--orange">
                  <Utensils size={20} />
                </div>
                <div>
                  <p className="floating-card__title">Warm Meals Fast</p>
                  <p className="floating-card__subtitle">Direct from campus cafes</p>
                </div>
              </div>

              <div className="hero__illustration-card">
                <div className="illustration-card__header">
                  <div className="illustration-card__tag">Campus Delivery Active</div>
                  <span className="illustration-card__price">Phase 1 Foundation</span>
                </div>
                <div className="illustration-card__body">
                  <div className="illustration-card__circle">
                    <Bike size={52} className="illustration-card__bike-icon" />
                  </div>
                  <h3 className="illustration-card__headline">Campus Byte Hub</h3>
                  <p className="illustration-card__text">
                    FastAPI + SQLAlchemy + PostgreSQL Backend Architecture
                  </p>
                </div>
                <div className="illustration-card__footer">
                  <div className="system-pill">React 18</div>
                  <div className="system-pill">Vite</div>
                  <div className="system-pill">FastAPI</div>
                  <div className="system-pill">Postgres 17</div>
                </div>
              </div>

              <div className="floating-card floating-card--bottom">
                <div className="floating-card__icon-badge floating-card__icon-badge--green">
                  <CheckCircle2 size={20} />
                </div>
                <div>
                  <p className="floating-card__title">Verified Delivery</p>
                  <p className="floating-card__subtitle">Dorm & Hallway PIN check</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stakeholders / Roles Section */}
      <section id="roles" className="roles-section">
        <div className="container">
          <div className="section-header">
            <span className="badge badge--primary">Ecosystem</span>
            <h2 className="section-header__title">Three Roles, One Campus Ecosystem</h2>
            <p className="section-header__subtitle">
              Every participant enjoys a tailored experience designed specifically for campus workflows.
            </p>
          </div>

          <div className="roles-grid">
            {roles.map((role) => {
              const RoleIcon = role.icon;
              return (
                <Card key={role.id} hoverable className="role-card">
                  <div className="role-card__header">
                    <div className={`role-card__icon role-card__icon--${role.badgeColor}`}>
                      <RoleIcon size={28} />
                    </div>
                    <span className={`badge badge--${role.badgeColor}`}>
                      {role.roleName}
                    </span>
                  </div>

                  <h3 className="role-card__title">{role.title}</h3>
                  <p className="role-card__tagline">{role.tagline}</p>

                  <ul className="role-card__features">
                    {role.features.map((feature, idx) => (
                      <li key={idx} className="role-card__feature-item">
                        <CheckCircle2 size={16} className="feature-check-icon" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="role-card__action">
                    <Link to={role.ctaLink} className="role-card__link">
                      <Button variant="secondary" size="md" className="btn--full" icon={ArrowRight}>
                        {role.ctaText}
                      </Button>
                    </Link>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Architecture Highlights */}
      <section id="tech-stack" className="tech-section">
        <div className="container">
          <div className="tech-card">
            <div className="tech-card__content">
              <span className="badge badge--secondary">Architecture Verified</span>
              <h3 className="tech-card__title">Modern Engineering Standards</h3>
              <p className="tech-card__desc">
                Engineered with high standards of decoupling, typed contracts, modular routing,
                and scalable containerization.
              </p>
              <div className="tech-card__grid">
                <div className="tech-item">
                  <span className="tech-item__name">Frontend</span>
                  <span className="tech-item__val">React 18 + Vite + SCSS</span>
                </div>
                <div className="tech-item">
                  <span className="tech-item__name">Routing & State</span>
                  <span className="tech-item__val">React Router DOM + Context</span>
                </div>
                <div className="tech-item">
                  <span className="tech-item__name">Backend Engine</span>
                  <span className="tech-item__val">FastAPI + Pydantic v2</span>
                </div>
                <div className="tech-item">
                  <span className="tech-item__name">Database ORM</span>
                  <span className="tech-item__val">SQLAlchemy 2.0 + Alembic</span>
                </div>
                <div className="tech-item">
                  <span className="tech-item__name">Data Store</span>
                  <span className="tech-item__val">PostgreSQL 17</span>
                </div>
                <div className="tech-item">
                  <span className="tech-item__name">Containers</span>
                  <span className="tech-item__val">Docker Compose Ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
