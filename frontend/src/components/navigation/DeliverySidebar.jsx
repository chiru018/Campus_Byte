import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Navigation,
  Package,
  History,
  User,
  LogOut,
  Bike,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function DeliverySidebar({
  courierName,
  vehicleType = 'BICYCLE',
  availabilityStatus = 'AVAILABLE',
  activeCount = 0,
  availableCount = 0,
}) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/', { replace: true });
  };

  const getStatusClass = (status) => {
    if (status === 'AVAILABLE') return 'delivery-status-pill--available';
    if (status === 'BUSY') return 'delivery-status-pill--busy';
    return 'delivery-status-pill--offline';
  };

  return (
    <aside className="delivery-layout__sidebar">
      <div className="delivery-courier-card">
        <h3 className="delivery-courier-card__name">{courierName || 'Student Courier'}</h3>
        <p className="delivery-courier-card__info">
          <Bike size={16} />
          <span>Mode: {vehicleType}</span>
        </p>
        <div style={{ marginTop: '0.75rem' }}>
          <span className={`delivery-status-pill ${getStatusClass(availabilityStatus)}`}>
            <span className="dot" />
            {availabilityStatus}
          </span>
        </div>
      </div>

      <nav className="delivery-nav">
        <NavLink
          to="/delivery/dashboard"
          end
          className={({ isActive }) =>
            `delivery-nav__link ${isActive ? 'delivery-nav__link--active' : ''}`
          }
        >
          <div className="link-inner">
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </div>
        </NavLink>

        <NavLink
          to="/delivery/available-orders"
          className={({ isActive }) =>
            `delivery-nav__link ${isActive ? 'delivery-nav__link--active' : ''}`
          }
        >
          <div className="link-inner">
            <Navigation size={18} />
            <span>Available Requests</span>
          </div>
          {availableCount > 0 && <span className="badge-count">{availableCount}</span>}
        </NavLink>

        <NavLink
          to="/delivery/active-delivery"
          className={({ isActive }) =>
            `delivery-nav__link ${isActive ? 'delivery-nav__link--active' : ''}`
          }
        >
          <div className="link-inner">
            <Package size={18} />
            <span>Active Delivery</span>
          </div>
          {activeCount > 0 && <span className="badge-count" style={{ background: '#F97316' }}>1</span>}
        </NavLink>

        <NavLink
          to="/delivery/history"
          className={({ isActive }) =>
            `delivery-nav__link ${isActive ? 'delivery-nav__link--active' : ''}`
          }
        >
          <div className="link-inner">
            <History size={18} />
            <span>Delivery History</span>
          </div>
        </NavLink>

        <NavLink
          to="/delivery/profile"
          className={({ isActive }) =>
            `delivery-nav__link ${isActive ? 'delivery-nav__link--active' : ''}`
          }
        >
          <div className="link-inner">
            <User size={18} />
            <span>Courier Profile</span>
          </div>
        </NavLink>
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid #E5E7EB' }}>
        <button
          onClick={handleLogout}
          className="delivery-nav__link"
          style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left' }}
        >
          <div className="link-inner" style={{ color: '#DC2626' }}>
            <LogOut size={18} />
            <span>Sign Out</span>
          </div>
        </button>
      </div>
    </aside>
  );
}

