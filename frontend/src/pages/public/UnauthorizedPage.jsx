import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, Home } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Button from '../../components/common/Button';
import './Auth.scss';

export default function UnauthorizedPage() {
  const { user, getRoleDashboard } = useAuth();
  const targetDashboard = user ? getRoleDashboard(user.role) : '/';

  return (
    <div className="auth-container">
      <div className="auth-card" style={{ textAlign: 'center' }}>
        <div
          className="auth-card__badge-icon"
          style={{ background: '#FEE2E2', color: '#DC2626' }}
        >
          <ShieldAlert size={28} />
        </div>
        <h2 className="auth-card__title">Access Restricted (403)</h2>
        <p className="auth-card__subtitle" style={{ marginBottom: '1.5rem' }}>
          You do not have the required role permissions to view this campus resource.
        </p>

        {user && (
          <div
            style={{
              padding: '0.75rem',
              background: '#F3F4F6',
              borderRadius: '8px',
              fontSize: '0.875rem',
              marginBottom: '1.5rem',
            }}
          >
            Signed in as: <strong>{user.email}</strong> (Role: <span style={{ color: '#F97316' }}>{user.role}</span>)
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <Link to={targetDashboard}>
            <Button variant="primary" size="md" icon={Home} style={{ width: '100%' }}>
              Return to My Role Dashboard
            </Button>
          </Link>
          <Link to="/">
            <Button variant="secondary" size="md" icon={ArrowLeft} style={{ width: '100%' }}>
              Campus Byte Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

