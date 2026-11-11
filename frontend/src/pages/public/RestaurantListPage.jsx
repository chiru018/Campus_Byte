import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Store,
  Search,
  MapPin,
  Phone,
  ArrowRight,
  UtensilsCrossed,
} from 'lucide-react';
import restaurantService from '../../services/restaurantService';
import Button from '../../components/common/Button';
import './Restaurants.scss';

export default function RestaurantListPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [search, setSearch] = useState('');
  const [isOpenFilter, setIsOpenFilter] = useState('');

  const fetchRestaurants = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = await restaurantService.getRestaurants({
        page: 1,
        size: 50,
        search,
        isOpen: isOpenFilter === '' ? null : isOpenFilter === 'true',
      });
      setRestaurants(data.restaurants || []);
      setTotal(data.total || 0);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to load campus restaurants.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRestaurants();
  }, [isOpenFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRestaurants();
  };

  return (
    <div className="restaurants-page">
      <div className="container">
        <div className="restaurants-page__header">
          <h1>Campus Dining & Food Outlets</h1>
          <p>
            Explore dining halls, cafes, food trucks, and local student favorites across the campus quad.
          </p>
        </div>

        {/* Controls */}
        <div className="restaurants-page__controls">
          <form onSubmit={handleSearchSubmit} className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search by restaurant name, food, or building location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </form>

          <select
            className="filter-select"
            value={isOpenFilter}
            onChange={(e) => setIsOpenFilter(e.target.value)}
          >
            <option value="">All Outlets</option>
            <option value="true">🟢 Open Now Only</option>
            <option value="false">🔴 Currently Closed</option>
          </select>

          <Button variant="primary" size="sm" onClick={fetchRestaurants}>
            Search
          </Button>
        </div>

        {errorMsg && (
          <div style={{ padding: '1rem', backgroundColor: '#FEE2E2', color: '#B91C1C', borderRadius: '0.75rem', marginBottom: '2rem' }}>
            {errorMsg}
          </div>
        )}

        {/* Content Grid */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <p>Loading campus restaurants...</p>
          </div>
        ) : restaurants.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '4rem 1rem', background: '#FFFFFF', borderRadius: '1rem', border: '1px dashed #E5E7EB' }}>
            <Store size={44} color="#9CA3AF" style={{ marginBottom: '1rem' }} />
            <h3>No Restaurants Found</h3>
            <p style={{ color: '#6B7280', maxWidth: '400px', margin: '0 auto 1.5rem auto' }}>
              No campus dining outlets match your search keyword or availability filter. Try clearing your filters.
            </p>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                setSearch('');
                setIsOpenFilter('');
                setTimeout(fetchRestaurants, 50);
              }}
            >
              Reset Filters
            </Button>
          </div>
        ) : (
          <div className="restaurants-page__grid">
            {restaurants.map((restaurant) => (
              <div key={restaurant.id} className="restaurant-card">
                <div className="restaurant-card__banner">
                  {restaurant.image_url ? (
                    <img
                      src={restaurant.image_url}
                      alt={restaurant.name}
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  ) : (
                    <div className="placeholder-banner">
                      <Store size={40} />
                    </div>
                  )}
                  <span
                    className={`status-badge ${
                      restaurant.is_open ? 'open' : 'closed'
                    }`}
                  >
                    {restaurant.is_open ? 'Open Now' : 'Closed'}
                  </span>
                </div>

                <div className="restaurant-card__content">
                  <h3>{restaurant.name}</h3>
                  <p>{restaurant.description || 'Quality meals prepared fresh on campus.'}</p>

                  <div className="restaurant-meta">
                    <div className="meta-item">
                      <MapPin size={14} />
                      <span>{restaurant.address}</span>
                    </div>
                    {restaurant.contact_number && (
                      <div className="meta-item">
                        <Phone size={14} />
                        <span>{restaurant.contact_number}</span>
                      </div>
                    )}
                  </div>

                  <Link to={`/restaurants/${restaurant.id}`} style={{ textDecoration: 'none' }}>
                    <Button variant="primary" size="sm" icon={UtensilsCrossed} style={{ width: '100%' }}>
                      View Full Menu
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

