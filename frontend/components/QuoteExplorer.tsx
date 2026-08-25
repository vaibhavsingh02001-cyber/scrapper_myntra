'use client';

import React, { useState, useEffect } from 'react';
import { api, VerbatimQuote } from '../lib/api';
import { Search, Filter, Star, Smartphone, ShoppingBag, MessageSquare, Quote as QuoteIcon } from 'lucide-react';

interface QuoteExplorerProps {
  selectedTheme: string;
  setSelectedTheme: (theme: string) => void;
}

const THEME_OPTIONS = [
  { key: 'all', label: 'All Themes' },
  { key: 'wishlist_discovery_intent', label: 'Wishlist & Discovery Intent' },
  { key: 'purchase_blockers', label: 'Purchase Blockers' },
  { key: 'fit_size_anxiety', label: 'Fit & Size Anxiety' },
  { key: 'price_value_sensitivity', label: 'Price & Value Sensitivity' },
  { key: 'social_occasion_validation', label: 'Social & Occasion Validation' },
  { key: 'cross_platform_research', label: 'Cross-Platform Research' },
  { key: 'comparison_shortlisting', label: 'Comparison & Shortlisting' },
  { key: 'post_purchase_feedback', label: 'Post-Purchase Regret / Validation' },
];

const DEFAULT_QUOTES: VerbatimQuote[] = [
  {
    text: "Saved 4 kurtas for the upcoming Diwali sale on Myntra. Adding them to cart early so I can checkout as soon as prices drop!",
    rating: 5,
    platform: "google_play",
    app_name: "Myntra",
    author: "Ananya S.",
    themes: ["wishlist_discovery_intent", "price_value_sensitivity"]
  },
  {
    text: "Wishlisted a medium size jacket, but it was out of stock within 10 minutes of notification. Needs better stock alerts.",
    rating: 2,
    platform: "app_store",
    app_name: "Myntra",
    author: "Rohan M.",
    themes: ["purchase_blockers", "wishlist_discovery_intent"]
  },
  {
    text: "Size chart on AJIO for trousers is super misleading. Said size 32 is 34 inch waist, but actually fits like size 30. Had to initiate return.",
    rating: 1,
    platform: "google_play",
    app_name: "AJIO",
    author: "Priya K.",
    themes: ["fit_size_anxiety", "purchase_blockers"]
  },
  {
    text: "Loved the quality of the wedding sherwani! Exactly as shown in the app photos. Delivery was super prompt within 2 days.",
    rating: 5,
    platform: "app_store",
    app_name: "Myntra",
    author: "Vikas P.",
    themes: ["social_occasion_validation", "post_purchase_feedback"]
  },
  {
    text: "Checked YouTube try-on haul before ordering this dress on AJIO. Glad I did because the color in reality is darker than online photo.",
    rating: 4,
    platform: "reddit",
    app_name: "Myntra/AJIO",
    author: "r/IndianFashionAddicts user",
    themes: ["cross_platform_research", "post_purchase_feedback"]
  },
  {
    text: "Shortlisted two black formal blazers on Myntra. Can't decide between Mango and Allen Solly. Wish there was a side-by-side comparison feature.",
    rating: 4,
    platform: "google_play",
    app_name: "Myntra",
    author: "Siddharth G.",
    themes: ["comparison_shortlisting", "wishlist_discovery_intent"]
  }
];

export const QuoteExplorer: React.FC<QuoteExplorerProps> = ({ selectedTheme, setSelectedTheme }) => {
  const [quotes, setQuotes] = useState<VerbatimQuote[]>(DEFAULT_QUOTES);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [platformFilter, setPlatformFilter] = useState<string>('all');

  useEffect(() => {
    const fetchQuotes = async () => {
      setLoading(true);
      try {
        const data = await api.getQuotes(
          selectedTheme,
          15,
          platformFilter === 'all' ? undefined : platformFilter
        );
        if (data.quotes && data.quotes.length > 0) {
          setQuotes(data.quotes);
        } else {
          setQuotes(DEFAULT_QUOTES.filter(q => selectedTheme === 'all' || q.themes?.includes(selectedTheme)));
        }
      } catch (err) {
        console.warn('API quotes fallback to default:', err);
        setQuotes(DEFAULT_QUOTES.filter(q => selectedTheme === 'all' || q.themes?.includes(selectedTheme)));
      } finally {
        setLoading(false);
      }
    };

    fetchQuotes();
  }, [selectedTheme, platformFilter]);

  const filteredQuotes = quotes.filter(q =>
    searchQuery === '' || q.text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div style={{ marginBottom: '40px' }}>
      
      {/* Filters Header */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
          
          {/* Theme Dropdown */}
          <div style={{ flex: '1 1 250px' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Filter by Behavioral Theme</label>
            <select
              value={selectedTheme}
              onChange={(e) => setSelectedTheme(e.target.value)}
              className="input-field"
              style={{ cursor: 'pointer' }}
            >
              {THEME_OPTIONS.map(opt => (
                <option key={opt.key} value={opt.key} style={{ background: '#0f172a' }}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Search Input */}
          <div style={{ flex: '1 1 300px', position: 'relative' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Search Keywords</label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                placeholder="e.g. out of stock, size chart, wedding..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field"
                style={{ paddingLeft: '40px' }}
              />
              <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
          </div>

          {/* Platform Pills */}
          <div>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Platform Source</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {['all', 'google_play', 'app_store', 'reddit'].map(p => (
                <button
                  key={p}
                  onClick={() => setPlatformFilter(p)}
                  className={`btn-secondary ${platformFilter === p ? 'active' : ''}`}
                  style={{
                    padding: '8px 14px',
                    fontSize: '0.8rem',
                    background: platformFilter === p ? 'rgba(236, 72, 153, 0.2)' : undefined,
                    borderColor: platformFilter === p ? '#ec4899' : undefined,
                    color: platformFilter === p ? '#f472b6' : undefined,
                  }}
                >
                  {p === 'all' && 'All Platforms'}
                  {p === 'google_play' && 'Google Play'}
                  {p === 'app_store' && 'App Store'}
                  {p === 'reddit' && 'Reddit'}
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Quote Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          <div className="pulsing-dot" style={{ margin: '0 auto 12px' }} />
          Loading verbatim review quotes...
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
          {filteredQuotes.map((quote, idx) => (
            <div key={idx} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderTop: '3px solid var(--accent-pink)' }}>
              <div>
                {/* Meta Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="badge badge-pink">
                      {quote.platform === 'google_play' && <Smartphone size={12} />}
                      {quote.platform === 'app_store' && <ShoppingBag size={12} />}
                      {quote.platform === 'reddit' && <MessageSquare size={12} />}
                      {quote.app_name || 'Myntra'}
                    </span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>by {quote.author || 'User'}</span>
                  </div>

                  {quote.rating && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#fbbf24', fontSize: '0.85rem', fontWeight: 700 }}>
                      <Star size={14} fill="#fbbf24" /> {quote.rating}
                    </div>
                  )}
                </div>

                {/* Quote Text */}
                <div style={{ fontSize: '0.95rem', color: '#f1f5f9', lineHeight: 1.6, fontStyle: 'italic', position: 'relative', paddingLeft: '20px', marginBottom: '16px' }}>
                  <QuoteIcon size={14} color="#ec4899" style={{ position: 'absolute', left: 0, top: '4px' }} />
                  "{quote.text}"
                </div>
              </div>

              {/* Theme Tags */}
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '12px' }}>
                {quote.themes?.map(t => (
                  <span key={t} className="badge badge-purple" style={{ fontSize: '0.7rem' }}>
                    #{t.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
