import React, { useState, useEffect } from 'react';
import { Store, Save, PlusCircle, CheckCircle, AlertCircle } from 'lucide-react';
import restaurantService from '../../services/restaurantService';
import RestaurantSidebar from '../../components/navigation/RestaurantSidebar';
import Button from '../../components/common/Button';
import './Restaurant.scss';

export default function RestaurantProfilePage() {
  const [restaurant, setRestaurant] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    address: '',
    contact_number: '',
    image_url: '',
    is_open: true,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isNew, setIsNew] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      setErrorMsg('');
      try {
        const data = await restaurantService.getMyRestaurant();
        setRestaurant(data);
        setFormData({
          name: data.name || '',
          description: data.description || '',
          address: data.address || '',
          contact_number: data.contact_number || '',
          image_url: data.image_url || '',
          is_open: data.is_open ?? true,
        });
      } catch (err) {
        if (err.response?.status === 404) {
          setIsNew(true);
        } else {
          setErrorMsg(err.response?.data?.detail || 'Failed to load restaurant profile.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

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
    setSuccessMsg('');
    setErrorMsg('');

    // Validation
    if (!formData.name.trim() || formData.name.length < 2) {
      setErrorMsg('Restaurant name must be at least 2 characters.');
      setSaving(false);
      return;
    }
    if (!formData.address.trim() || formData.address.length < 3) {
      setErrorMsg('Address must be at least 3 characters.');
      setSaving(false);
      return;
    }
    if (!formData.contact_number.trim() || formData.contact_number.length < 5) {
      setErrorMsg('Contact number must be at least 5 characters.');
      setSaving(false);
      return;
    }

    try {
      if (isNew) {
        const created = await restaurantService.createRestaurant(formData);
        setRestaurant(created);
        setIsNew(false);
        setSuccessMsg('Restaurant profile created successfully!');
      } else {
        const updated = await restaurantService.updateRestaurant(restaurant.id, formData);
        setRestaurant(updated);
        setSuccessMsg('Restaurant profile updated successfully!');
      }
    } catch (err) {
      setErrorMsg(
        err.response?.data?.detail || 'An error occurred while saving profile changes.'
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="restaurant-layout">
        <div style={{ padding: '3rem', textAlign: 'center', width: '100%' }}>
          <p>Loading profile...</p>
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
            <h1>{isNew ? 'Register Restaurant Profile' : 'Restaurant Profile Management'}</h1>
            <p>Configure public campus food outlet details, address, and live availability.</p>
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

        <form onSubmit={handleSubmit} className="form-card">
          <h3 className="form-card__title">Outlet Information</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Restaurant Name *</label>
              <input
                id="name"
                name="name"
                type="text"
                placeholder="e.g. Student Canteen Grill"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_number">Phone / Contact Number *</label>
              <input
                id="contact_number"
                name="contact_number"
                type="text"
                placeholder="e.g. +1 555 123 4567"
                value={formData.contact_number}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="address">Campus Physical Location / Address *</label>
            <input
              id="address"
              name="address"
              type="text"
              placeholder="e.g. Student Union Building, Ground Floor, Booth 2"
              value={formData.address}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Cuisine & Description</label>
            <textarea
              id="description"
              name="description"
              placeholder="Describe your dishes, specialties, dietary options..."
              value={formData.description}
              onChange={handleChange}
            ></textarea>
          </div>

          <div className="form-group">
            <label htmlFor="image_url">Storefront / Logo Image URL</label>
            <input
              id="image_url"
              name="image_url"
              type="url"
              placeholder="https://images.unsplash.com/photo-..."
              value={formData.image_url}
              onChange={handleChange}
            />
          </div>

          <div className="form-group" style={{ marginTop: '1rem' }}>
            <label className="toggle-switch">
              <input
                type="checkbox"
                name="is_open"
                checked={formData.is_open}
                onChange={handleChange}
              />
              <span className="switch-slider"></span>
              <span className="toggle-label" style={{ fontSize: '0.9rem' }}>
                Open for Customer Orders
              </span>
            </label>
          </div>

          <div className="form-actions">
            <Button
              type="submit"
              variant="primary"
              icon={isNew ? PlusCircle : Save}
              disabled={saving}
            >
              {saving ? 'Saving...' : isNew ? 'Create Restaurant' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}

