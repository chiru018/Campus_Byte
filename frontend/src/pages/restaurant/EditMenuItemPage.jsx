import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Save, ArrowLeft, AlertCircle } from 'lucide-react';
import restaurantService from '../../services/restaurantService';
import menuService from '../../services/menuService';
import RestaurantSidebar from '../../components/navigation/RestaurantSidebar';
import Button from '../../components/common/Button';
import './Restaurant.scss';

export default function EditMenuItemPage() {
  const { itemId } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: '',
    image_url: '',
    is_available: true,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    const fetchItemAndContext = async () => {
      setLoading(true);
      setErrorMsg('');
      try {
        const rest = await restaurantService.getMyRestaurant();
        setRestaurant(rest);

        const catList = await menuService.getCategories();
        setCategories(catList);

        const itemData = await menuService.getMenuItem(itemId);
        setFormData({
          name: itemData.name || '',
          description: itemData.description || '',
          price: itemData.price || '',
          category: itemData.category || (catList[0]?.key ?? 'OTHER'),
          image_url: itemData.image_url || '',
          is_available: itemData.is_available ?? true,
        });
      } catch (err) {
        setErrorMsg(err.response?.data?.detail || 'Failed to load menu item details.');
      } finally {
        setLoading(false);
      }
    };

    fetchItemAndContext();
  }, [itemId]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');

    if (!formData.name.trim()) {
      setErrorMsg('Dish name is required.');
      setSaving(false);
      return;
    }
    const numPrice = parseFloat(formData.price);
    if (isNaN(numPrice) || numPrice <= 0) {
      setErrorMsg('Price must be greater than $0.00.');
      setSaving(false);
      return;
    }

    try {
      const payload = {
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        price: numPrice.toFixed(2),
        category: formData.category,
        image_url: formData.image_url.trim() || null,
        is_available: formData.is_available,
      };

      await menuService.updateMenuItem(itemId, payload);
      navigate('/restaurant/menu');
    } catch (err) {
      setErrorMsg(
        err.response?.data?.detail || 'Failed to update menu item. Please check inputs.'
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="restaurant-layout">
        <div style={{ padding: '3rem', textAlign: 'center', width: '100%' }}>
          <p>Loading item details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="restaurant-layout">
      <RestaurantSidebar
        restaurantName={restaurant?.name}
        isOpen={restaurant?.is_open}
      />

      <main className="restaurant-content">
        <div className="restaurant-content__header">
          <div>
            <Link
              to="/restaurant/menu"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
                color: '#6B7280',
                fontSize: '0.85rem',
                marginBottom: '0.5rem',
                textDecoration: 'none',
              }}
            >
              <ArrowLeft size={16} /> Back to Menu
            </Link>
            <h1>Edit Food Item</h1>
            <p>Update dish pricing, availability, and description.</p>
          </div>
        </div>

        {errorMsg && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem', backgroundColor: '#FEE2E2', color: '#B91C1C', borderRadius: '0.75rem', marginBottom: '1.5rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="form-card">
          <h3 className="form-card__title">Edit Item Details</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Item / Dish Name *</label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="price">Price ($ USD) *</label>
              <input
                id="price"
                name="price"
                type="number"
                step="0.01"
                min="0.01"
                value={formData.price}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category">Category *</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                required
              >
                {categories.map((c) => (
                  <option key={c.key} value={c.key}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="image_url">Presentation Image URL</label>
              <input
                id="image_url"
                name="image_url"
                type="url"
                value={formData.image_url}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Ingredients & Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
            ></textarea>
          </div>

          <div className="form-group" style={{ marginTop: '0.5rem' }}>
            <label className="toggle-switch">
              <input
                type="checkbox"
                name="is_available"
                checked={formData.is_available}
                onChange={handleChange}
              />
              <span className="switch-slider"></span>
              <span className="toggle-label" style={{ fontSize: '0.9rem' }}>
                Item is In Stock & Available to Order
              </span>
            </label>
          </div>

          <div className="form-actions">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/restaurant/menu')}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              icon={Save}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}
