import React from 'react';
import { UtensilsCrossed, Heart, ShieldCheck, Zap } from 'lucide-react';
import './Footer.scss';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer__container">
        <div className="footer__brand-col">
          <div className="footer__brand">
            <div className="footer__logo-badge">
              <UtensilsCrossed size={18} />
            </div>
            <span className="footer__brand-name">Campus Byte</span>
          </div>
          <p className="footer__description">
            Next-generation campus food delivery platform engineered for students,
            campus eateries, and campus delivery partners.
          </p>
          <div className="footer__badges">
            <span className="badge badge--success">
              <Zap size={12} /> Phase 1 Foundation Active
            </span>
            <span className="badge badge--secondary">
              <ShieldCheck size={12} /> FastAPI + PostgreSQL + React
            </span>
          </div>
        </div>

        <div className="footer__links-col">
          <h4 className="footer__heading">Platform Stakeholders</h4>
          <ul className="footer__link-list">
            <li><a href="#roles">Student Customers</a></li>
            <li><a href="#roles">Restaurant Partners</a></li>
            <li><a href="#roles">Delivery Fleet</a></li>
            <li><a href="#roles">Campus Admins</a></li>
          </ul>
        </div>

        <div className="footer__links-col">
          <h4 className="footer__heading">Architecture</h4>
          <ul className="footer__link-list">
            <li><a href="#tech-stack">FastAPI Backend (v1)</a></li>
            <li><a href="#tech-stack">React 18 + Vite</a></li>
            <li><a href="#tech-stack">SQLAlchemy ORM</a></li>
            <li><a href="#tech-stack">PostgreSQL 17 Database</a></li>
          </ul>
        </div>
      </div>

      <div className="footer__bottom">
        <div className="container footer__bottom-container">
          <p className="footer__copyright">
            &copy; {new Date().getFullYear()} Campus Byte. All rights reserved.
          </p>
          <p className="footer__crafted">
            Engineered with <Heart size={14} className="footer__heart" /> for college campuses
          </p>
        </div>
      </div>
    </footer>
  );
}

