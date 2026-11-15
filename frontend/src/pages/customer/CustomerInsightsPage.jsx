import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  TrendingUp,
  ShoppingBag,
  DollarSign,
  Utensils,
  Award,
  RefreshCw,
  Plus,
  Check,
  Calendar,
  Store,
  ChevronRight,
} from 'lucide-react';
import insightsService from '../../services/insightsService';
import { useCart } from '../../context/CartContext';
import Button from '../../components/common/Button';
import './CustomerInsights.scss';

export default function CustomerInsightsPage() {
  const [summary, setSummary] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [aiNarrative, setAiNarrative] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [addedItems, setAddedItems] = useState({});

  const { addToCart } = useCart();

  const fetchAllInsights = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const [sumRes, patRes, recRes, aiRes] = await Promise.all([
        insightsService.getSpendingSummary(),
        insightsService.getOrderingPatterns(),
        insightsService.getRecommendations(6),
        insightsService.getAiSummary(),
      ]);

      setSummary(sumRes);
      setPatterns(patRes);
      setRecommendations(recRes.recommendations || []);
      setAiNarrative(aiRes);
    } catch (err) {
      console.error('Insights error:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load your dining insights.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllInsights();
  }, []);

  const handleAddToCart = (dish) => {
    addToCart(
      {
        id: dish.menu_item_id,
        name: dish.dish_name,
        price: parseFloat(dish.price),
        category: dish.category,
        image_url: dish.image_url,
      },
      {
        id: dish.restaurant_id,
        name: dish.restaurant_name,
      }
    );

    setAddedItems((prev) => ({ ...prev, [dish.menu_item_id]: true }));
    setTimeout(() => {
      setAddedItems((prev) => ({ ...prev, [dish.menu_item_id]: false }));
    }, 1800);
  };

  if (loading) {
    return (
      <div className="insights-page">
        <div className="container" style={{ textAlign: 'center', padding: '6rem 0' }}>
          <Sparkles size={40} className="spinner" style={{ color: '#6366f1', marginBottom: '1rem', animation: 'spin 2s linear infinite' }} />
          <h2>Analyzing your dining habits with AI...</h2>
          <p style={{ color: '#64748b' }}>Synthesizing spending history and tailoring personalized recommendations.</p>
        </div>
      </div>
    );
  }

  const topRestaurant = patterns?.favourite_restaurants?.[0]?.restaurant_name || 'Campus Outlets';

  return (
    <div className="insights-page">
      <div className="container">
        {/* Header */}
        <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div className="header-badge">
              <Sparkles size={14} /> AI-Powered Analytics
            </div>
            <h1>Your Campus Dining Insights</h1>
            <p>Smart breakdown of your meal trends, campus favorites, and Gemini-driven recommendations</p>
          </div>
          <button
            type="button"
            onClick={fetchAllInsights}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: '#FFFFFF',
              border: '1px solid #CBD5E1',
              borderRadius: '0.5rem',
              padding: '0.5rem 0.85rem',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#475569',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={15} /> Refresh Insights
          </button>
        </div>

        {errorMsg && (
          <div style={{ background: '#FEF2F2', color: '#991B1B', padding: '1rem', borderRadius: '0.75rem', marginBottom: '1.5rem' }}>
            {errorMsg}
          </div>
        )}

        {/* AI Narrative Hero Banner */}
        {aiNarrative && (
          <div className="ai-narrative-card">
            <div className="ai-header">
              <div className="ai-title-wrap">
                <Sparkles size={22} color="#a5b4fc" />
                <h2>AI Executive Summary</h2>
              </div>
              <span className="engine-pill">
                Powered by {aiNarrative.source === 'gemini' ? 'Google Gemini 2.5 Flash' : 'Campus Byte AI Engine'}
              </span>
            </div>

            <p className="ai-narrative-text">{aiNarrative.narrative}</p>

            {aiNarrative.key_highlights && aiNarrative.key_highlights.length > 0 && (
              <div className="ai-highlights">
                {aiNarrative.key_highlights.map((highlight, idx) => (
                  <div key={idx} className="highlight-chip">
                    <Award size={16} color="#fbbf24" />
                    <span>{highlight}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Quick Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon stat-icon--spend">
              <DollarSign size={26} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Total Spend</div>
              <div className="stat-val">₹{parseFloat(summary?.total_spent || 0).toFixed(2)}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon stat-icon--orders">
              <ShoppingBag size={26} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Orders Placed</div>
              <div className="stat-val">{summary?.completed_orders || summary?.total_orders || 0}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon stat-icon--avg">
              <TrendingUp size={26} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Average Meal Cost</div>
              <div className="stat-val">₹{parseFloat(summary?.average_order_value || 0).toFixed(2)}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon stat-icon--fav">
              <Store size={26} />
            </div>
            <div className="stat-content">
              <div className="stat-label">Top Dining Spot</div>
              <div className="stat-val" style={{ fontSize: '1.15rem' }}>{topRestaurant}</div>
            </div>
          </div>
        </div>

        {/* Two-Column Analytics */}
        <div className="insights-two-col">
          {/* Monthly Spending History */}
          <div className="panel-card">
            <h3>
              <Calendar size={18} color="#4f46e5" /> Monthly Spending Trends
            </h3>
            {summary?.monthly_spending?.length > 0 ? (
              <div className="monthly-trend-list">
                {summary.monthly_spending.map((item, idx) => (
                  <div key={idx} className="trend-row">
                    <span className="month-name">{item.month}</span>
                    <div className="month-metrics">
                      <span className="order-badge">{item.order_count} {item.order_count === 1 ? 'order' : 'orders'}</span>
                      <span className="month-spend">₹{parseFloat(item.amount).toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                No completed monthly orders recorded yet. Order delicious meals to see trends here!
              </p>
            )}
          </div>

          {/* Top Favorite Dishes */}
          <div className="panel-card">
            <h3>
              <Utensils size={18} color="#059669" /> Your Most-Ordered Dishes
            </h3>
            {patterns?.top_dishes?.length > 0 ? (
              <div className="top-dishes-list">
                {patterns.top_dishes.map((dish, idx) => (
                  <div key={idx} className="dish-row">
                    <div>
                      <div className="dish-name">{dish.dish_name}</div>
                      <div className="dish-cat">{dish.category}</div>
                    </div>
                    <div className="dish-stats">
                      <div className="dish-qty">{dish.total_quantity}x ordered</div>
                      <div className="dish-spend">₹{parseFloat(dish.total_spent).toFixed(2)}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                Your favorite dishes will appear here after your first completed orders!
              </p>
            )}
          </div>
        </div>

        {/* Personalized AI Recommendations */}
        <div className="recommendations-section">
          <div className="section-header">
            <div>
              <h2>
                <Sparkles size={20} color="#6366f1" /> Recommended For You
              </h2>
              <p>Curated meals matching your dining frequency and culinary preferences</p>
            </div>
            <Link to="/restaurants">
              <Button variant="outline" size="small" icon={ChevronRight}>
                View All Outlets
              </Button>
            </Link>
          </div>

          {recommendations.length > 0 ? (
            <div className="recommendations-grid">
              {recommendations.map((dish) => (
                <div key={dish.menu_item_id} className="recommendation-card">
                  <div
                    className="card-img"
                    style={{
                      backgroundImage: dish.image_url ? `url(${dish.image_url})` : 'none',
                    }}
                  >
                    <span className="reason-badge">✨ {dish.reason}</span>
                  </div>

                  <div className="card-body">
                    <h4 className="dish-title">{dish.dish_name}</h4>
                    <span className="rest-subtitle">{dish.restaurant_name}</span>

                    <div className="card-footer">
                      <span className="price">₹{parseFloat(dish.price).toFixed(2)}</span>
                      <Button
                        variant={addedItems[dish.menu_item_id] ? 'secondary' : 'primary'}
                        size="small"
                        icon={addedItems[dish.menu_item_id] ? Check : Plus}
                        onClick={() => handleAddToCart(dish)}
                      >
                        {addedItems[dish.menu_item_id] ? 'Added' : 'Add to Cart'}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#94a3b8', textAlign: 'center', padding: '2rem 0' }}>
              No recommendations available currently. Check back shortly!
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

