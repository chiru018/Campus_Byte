import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Store,
  UtensilsCrossed,
  PlusCircle,
  ClipboardList,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function RestaurantSidebar({ restaurantName, isOpen, pendingCount = 0 }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/', { replace: true });
  };

  return (
    <aside className="restaurant-sidebar">
      <div className="restaurant-sidebar__header">
        <Store size={28} className="sidebar-icon" />
        <div>
          <h3>{restaurantName || 'My Restaurant'}</h3>
          <p>{isOpen ? '🟢 Open for Orders' : '🔴 Currently Closed'}</p>
        </div>
      </div>

      <nav className="restaurant-sidebar__nav">
        <NavLink
          to="/restaurant/dashboard"
          end
          className={({ isActive }) =>
            `restaurant-sidebar__link ${isActive ? 'active' : ''}`
          }
        >
          <LayoutDashboard size={18} />
          <span>Overview</span>
        </NavLink>

        <NavLink
          to="/restaurant/orders"
          className={({ isActive }) =>
            `restaurant-sidebar__link ${isActive ? 'active' : ''}`
          }
        >
          <ClipboardList size={18} />
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
            <span>Orders</span>
            {pendingCount > 0 && (
              <span
                style={{
                  background: '#EF4444',
                  color: '#FFFFFF',
                  borderRadius: '9999px',
                  padding: '2px 7px',
                  fontSize: '0.75rem',
                  fontWeight: '700',
                }}
              >
                {pendingCount}
              </span>
            )}
          </span>
        </NavLink>

        <NavLink
          to="/restaurant/profile"
          className={({ isActive }) =>
            `restaurant-sidebar__link ${isActive ? 'active' : ''}`
          }
        >
          <Store size={18} />
          <span>Restaurant Profile</span>
        </NavLink>

        <NavLink
          to="/restaurant/menu"
          end
          className={({ isActive }) =>
            `restaurant-sidebar__link ${isActive ? 'active' : ''}`
          }
        >
          <UtensilsCrossed size={18} />
          <span>Menu Management</span>
        </NavLink>

        <NavLink
          to="/restaurant/menu/add"
          className={({ isActive }) =>
            `restaurant-sidebar__link ${isActive ? 'active' : ''}`
          }
        >
          <PlusCircle size={18} />
          <span>Add Food Item</span>
        </NavLink>
      </nav>

      <div className="restaurant-sidebar__footer">
        <button
          type="button"
          onClick={handleLogout}
          className="restaurant-sidebar__link"
          style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left' }}
        >
          <LogOut size={18} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
