import React from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { ArrowLeft, UserPlus } from 'lucide-react';

export default function RegisterPage() {
  const [searchParams] = useSearchParams();
  const selectedRole = searchParams.get('role') || 'customer';

  return (
    <div className="container" style={{ padding: '4rem 1rem', maxWidth: '480px' }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div
            style={{
              width: '48px',
              height: '48px',
              background: '#FFEDD5',
              color: '#F97316',
              borderRadius: '12px',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem',
            }}
          >
            <UserPlus size={24} />
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1F2937' }}>
            Create Account
          </h2>
          <span
            style={{
              display: 'inline-block',
              marginTop: '0.5rem',
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              backgroundColor: '#F3F4F6',
              color: '#1F2937',
            }}
          >
            Role: {selectedRole}
          </span>
          <p style={{ color: '#4B5563', fontSize: '0.875rem', marginTop: '0.75rem' }}>
            Registration workflows and role-based onboarding will be unlocked in subsequent phases.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Link to="/">
            <Button variant="secondary" size="md" icon={ArrowLeft} style={{ width: '100%' }}>
              Back to Home
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
