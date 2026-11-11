import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  UtensilsCrossed,
  PlusCircle,
  Search,
  Edit2,
  Trash2,
  AlertCircle,
  CheckCircle,
  Tag,
} from 'lucide-react';
import restaurantService from '../../services/restaurantService';
import menuService from '../../services/menuService';
import RestaurantSidebar from '../../components/navigation/RestaurantSidebar';
import Button from '../../components/common/Button';
import './Restaurant.scss';

export default function MenuManagementPage() {
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [availabilityFilter, setAvailabilityFilter] = useState('');

  const navigate = useNavigate();

  const loadData = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const rest = await restaurantService.getMyRestaurant();
      setRestaurant(rest);

      // Load categories
      try {
        const catList = await menuService.getCategories();
        setCategories(catList);
      } catch (err) {
        console.warn('Could not load categories list:', err);
      }

      // Load menu items
      if (rest?.id) {
        const menuData = await menuService.getRestaurantMenu(rest.id, {
          search: searchTerm,
          category: selectedCategory,
          isAvailable: availabilityFilter === '' ? null : availabilityFilter === 'true',
        });
        setMenuItems(menuData.items || []);
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setRestaurant(null);
      } else {
        setErrorMsg(err.response?.data?.detail || 'Failed to load restaurant menu.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedCategory, availabilityFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  const handleToggleItemAvailability = async (item) => {
    try {
      const newStatus = !item.is_available;
      await menuService.updateMenuItemAvailability(item.id, newStatus);
      setMenuItems((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, is_available: newStatus } : i))
      );
      setSuccessMsg(`Updated availability for "${item.name}".`);
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Could not update item availability.');
    }
  };

  const handleDeleteItem = async (item) => {
    if (!window.confirm(`Are you sure you want to remove "${item.name}"? If it exists in previous orders, it will be deactivated to protect history.`)) {
      return;
    }

    try {
      const res = await menuService.deleteMenuItem(item.id);
      if (res.is_deactivated) {
        setMenuItems((prev) =>
          prev.map((i) => (i.id === item.id ? { ...i, is_available: false } : i))
        );
        setSuccessMsg(res.message);
      } else {
        setMenuItems((prev) => prev.filter((i) => i.id !== item.id));
        setSuccessMsg(`"${item.name}" was successfully removed.`);
      }
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Could not remove menu item.');
    }
  };

  if (loading && !restaurant) {
    return (
      <div className="restaurant-layout">
        <div style={{ padding: '3rem', textAlign: 'center', width: '100%' }}>
          <p>Loading menu management...</p>
        </div>
      </div>
    );
  }

  if (!restaurant) {
    return (
      <div className="restaurant-layout">
        <div className="restaurant-content" style={{ margin: '0 auto' }}>
          <div className="empty-state">
            <UtensilsCrossed size={48} />
            <h3>No Restaurant Registered</h3>
            <p>Please register your restaurant outlet before managing food items.</p>
            <Link to="/restaurant/profile">
              <Button variant="primary">Register Restaurant</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="restaurant-layout">
      <RestaurantSidebar
        restaurantName={restaurant.name}
        isOpen={restaurant.is_open}
      />

      <main className="restaurant-content">
        <div className="restaurant-content__header">
          <div>
            <h1>Menu Catalog Management</h1>
            <p>Add, update, adjust prices, and toggle in-stock availability of your dishes.</p>
          </div>

          <div className="header-actions">
            <Link to="/restaurant/menu/add">
              <Button variant="primary" size="sm" icon={PlusCircle}>
                Add New Dish
              </Button>
            </Link>
          </div>
        </div>

        {successMsg && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem', backgroundColor: '#ECFDF5', color: '#065F46', borderRadius: '0.75rem', marginBottom: '1.5rem' }}>
            <CheckCircle size={18} />
            <span>{successMsg}</span>
          </div>
        )}

        {errorMsg && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem', backgroundColor: '#FEE2E2', color: '#B91C1C', borderRadius: '0.75rem', marginBottom: '1.5rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Filter and Search Bar */}
        <div className="filter-bar">
          <form onSubmit={handleSearchSubmit} className="search-input">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search dishes by name or ingredients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </form>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.key} value={c.key}>
                {c.label}
              </option>
            ))}
          </select>

          <select
            value={availabilityFilter}
            onChange={(e) => setAvailabilityFilter(e.target.value)}
          >
            <option value="">All Stock States</option>
            <option value="true">Available / In Stock</option>
            <option value="false">Unavailable / Sold Out</option>
          </select>
        </div>

        {/* Menu Items Grid */}
        {menuItems.length === 0 ? (
          <div className="empty-state">
            <UtensilsCrossed size={44} />
            <h3>No Food Items Found</h3>
            <p>
              {searchTerm || selectedCategory || availabilityFilter
                ? 'No items matched your current search filters. Try clearing your filters.'
                : 'Your menu catalog is currently empty. Start adding dishes for campus diners!'}
            </p>
            <Link to="/restaurant/menu/add">
              <Button variant="primary" icon={PlusCircle}>
                Add First Menu Item
              </Button>
            </Link>
          </div>
        ) : (
          <div className="menu-grid">
            {menuItems.map((item) => (
              <div key={item.id} className="menu-card">
                <div className="menu-card__image-wrap">
                  {item.image_url ? (
                    <img src={item.image_url} alt={item.name} onError={(e) => { e.target.style.display = 'none'; }} />
                  ) : (
                    <div className="placeholder-img">
                      <UtensilsCrossed size={32} />
                    </div>
                  )}
                  <span className="badge-category">{item.category}</span>
                  <span
                    className={`badge-availability ${
                      item.is_available ? 'available' : 'unavailable'
                    }`}
                  >
                    {item.is_available ? 'In Stock' : 'Out of Stock'}
                  </span>
                </div>

                <div className="menu-card__body">
                  <h3>{item.name}</h3>
                  <p>{item.description || 'No description provided.'}</p>

                  <div className="price-row">
                    <span className="price">${parseFloat(item.price).toFixed(2)}</span>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={item.is_available}
                        onChange={() => handleToggleItemAvailability(item)}
                      />
                      <span className="switch-slider"></span>
                      <span className="toggle-label">
                        {item.is_available ? 'Available' : 'Unavailable'}
                      </span>
                    </label>
                  </div>
                </div>

                <div className="menu-card__actions">
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={Edit2}
                    onClick={() => navigate(`/restaurant/menu/edit/${item.id}`)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={Trash2}
                    onClick={() => handleDeleteItem(item)}
                    style={{ color: '#EF4444' }}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
