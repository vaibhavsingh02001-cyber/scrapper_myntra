'use client';

import React from 'react';
import { ThemesOverview } from '../lib/api';
import { Heart, AlertTriangle, Ruler, Tag, Users, Search, GitCompare, MessageSquare } from 'lucide-react';

interface ThemeHeatmapProps {
  overview: ThemesOverview | null;
  onSelectTheme: (themeKey: string) => void;
}

const THEME_ICONS: Record<string, React.ReactNode> = {
  wishlist_discovery_intent: <Heart size={20} color="#ec4899" />,
  purchase_blockers: <AlertTriangle size={20} color="#ef4444" />,
  fit_size_anxiety: <Ruler size={20} color="#f59e0b" />,
  price_value_sensitivity: <Tag size={20} color="#10b981" />,
  social_occasion_validation: <Users size={20} color="#a78bfa" />,
  cross_platform_research: <Search size={20} color="#06b6d4" />,
  comparison_shortlisting: <GitCompare size={20} color="#60a5fa" />,
  post_purchase_feedback: <MessageSquare size={20} color="#f472b6" />,
};

const DEFAULT_THEMES_DATA = [
  { key: 'wishlist_discovery_intent', label: 'Wishlist & Discovery Intent', count: 3450, pct: 34.5, rating: 4.2, desc: 'Why users save/wishlist fashion products rather than buying immediately', quote: 'Saved 5 dresses for my birthday next month. Waiting to see if prices drop!' },
  { key: 'purchase_blockers', label: 'Purchase Blockers', count: 2180, pct: 21.8, rating: 2.1, desc: 'Out of stock, non-returnable items, delivery delays stopping conversion', quote: 'Item went out of stock right while in my cart. Very frustrating.' },
  { key: 'fit_size_anxiety', label: 'Fit & Size Anxiety', count: 1840, pct: 18.4, rating: 2.8, desc: 'Size chart mismatch, runs small/large, fit uncertainty causing hesitation', quote: 'Size chart said M but it fits like XS. Sizing is super inconsistent.' },
  { key: 'price_value_sensitivity', label: 'Price & Value Sensitivity', count: 1420, pct: 14.2, rating: 3.5, desc: 'Waiting for sale discounts, coupon issues, value judgements', quote: 'Overpriced at MRP. Will only order during End of Reason Sale.' },
  { key: 'social_occasion_validation', label: 'Social & Occasion Validation', count: 960, pct: 9.6, rating: 4.5, desc: 'Wedding wear, office outfits, influencer looks, gifts', quote: 'Needed a wedding guest kurta urgently. Found great styling photos!' },
  { key: 'cross_platform_research', label: 'Cross-Platform Research', count: 720, pct: 7.2, rating: 3.8, desc: 'Checking YouTube haul reviews, Instagram reels, Google search before buying', quote: 'Checked YouTube try-on haul before ordering to verify exact color.' },
  { key: 'comparison_shortlisting', label: 'Comparison & Shortlisting', count: 540, pct: 5.4, rating: 4.0, desc: 'Comparing 2-3 shortlisted items, undecisiveness between options', quote: 'Shortlisted two black blazer options on Myntra and AJIO, comparing fit.' },
  { key: 'post_purchase_feedback', label: 'Post-Purchase Regret / Validation', count: 890, pct: 8.9, rating: 3.2, desc: 'Fabric quality feedback, color mismatch from app photos', quote: 'Fabric is very thin compared to how vibrant it looks on screen.' },
];

export const ThemeHeatmap: React.FC<ThemeHeatmapProps> = ({ overview, onSelectTheme }) => {
  const themesDict = overview?.themes;

  return (
    <div style={{ marginBottom: '40px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>8 Strategic Behavioral Themes</span>
            <span className="badge badge-pink">Live Analytics</span>
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Classified across thousands of Myntra & AJIO customer reviews
          </p>
        </div>
      </div>

      {/* Grid of 8 Theme Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {DEFAULT_THEMES_DATA.map((defTheme) => {
          const liveData = themesDict ? themesDict[defTheme.key] : null;
          const count = liveData ? liveData.review_count : defTheme.count;
          const pct = liveData ? liveData.percentage : defTheme.pct;
          const rating = liveData?.avg_rating ?? defTheme.rating;
          const sampleQuote = liveData?.verbatim_quotes?.[0] ?? defTheme.quote;

          return (
            <div
              key={defTheme.key}
              className="glass-panel"
              style={{
                padding: '24px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
              onClick={() => onSelectTheme(defTheme.key)}
            >
              <div>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ padding: '8px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)' }}>
                      {THEME_ICONS[defTheme.key]}
                    </div>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>
                      {defTheme.label}
                    </h3>
                  </div>
                  <span className="badge badge-purple" style={{ fontSize: '0.8rem' }}>
                    {pct}%
                  </span>
                </div>

                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '16px', lineHeight: 1.4 }}>
                  {defTheme.desc}
                </p>

                {/* Progress bar */}
                <div style={{ marginBottom: '16px' }}>
                  <div className="progress-bar-bg">
                    <div className="progress-bar-fill" style={{ width: `${Math.min(pct * 2, 100)}%` }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
                    <span>{count.toLocaleString()} reviews</span>
                    <span>Avg Rating: ★ {rating ? rating.toFixed(1) : 'N/A'}</span>
                  </div>
                </div>

                {/* Verbatim quote preview */}
                <div style={{ background: 'rgba(15, 23, 42, 0.9)', padding: '12px', borderRadius: '10px', borderLeft: '3px solid var(--accent-pink)', fontSize: '0.8rem', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                  "{sampleQuote}"
                </div>
              </div>

              <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f472b6', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  Explore Quotes &rarr;
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
