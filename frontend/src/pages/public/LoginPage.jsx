import React from 'react';
import { Link } from 'react-router-dom';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { ArrowLeft, Lock } from 'lucide-react';

export default function LoginPage() {
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
            <Lock size={24} />
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1F2937' }}>
            Sign In to Campus Byte
          </h2>
          <p style={{ color: '#4B5563', fontSize: '0.875rem', marginTop: '0.5rem' }}>
            Authentication & JWT modules will be activated in Phase 2.
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

