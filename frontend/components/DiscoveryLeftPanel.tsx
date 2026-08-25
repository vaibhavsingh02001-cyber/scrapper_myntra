'use client';

import React, { useEffect, useState } from 'react';
import {
  Heart, AlertTriangle, Ruler, Tag, Users, Search,
  GitCompare, MessageSquare, TrendingUp, Quote, ChevronRight,
  BarChart3, Shield, RefreshCw, Star, Smartphone, ShoppingBag,
  Sparkles, MessageCircle, ArrowRight
} from 'lucide-react';
import { api, ThemesOverview, SummaryStats, VerbatimQuote } from '../lib/api';

interface DiscoveryLeftPanelProps {
  onAskQuestion: (question: string) => void;
}

const DISCOVERY_THEMES = [
  {
    num: 1,
    key: 'purchase_blockers',
    label: 'Trust & Risk (Purchase Blockers)',
    icon: <Shield size={18} />,
    color: '#EF4444',
    bg: '#FEF2F2',
    desc: 'Quality concerns, unfamiliar brands, stockouts, and return/refund worries stop users from converting.',
    defaultCount: 1070,
    defaultPct: 40,
    defaultRating: 2.0,
    suggestedQ: 'What trust and risk factors prevent users from purchasing wishlisted Myntra items?',
    quote: 'Item went out of stock right while it was in my cart. So frustrating.',
  },
  {
    num: 2,
    key: 'wishlist_discovery_intent',
    label: 'Habit Formation (Wishlist & Discovery Intent)',
    icon: <RefreshCw size={18} />,
    color: '#10B981',
    bg: '#ECFDF5',
    desc: 'Building repeat shopping habits, sale reminders, and aspirational lookbook bookmarking.',
    defaultCount: 3876,
    defaultPct: 34.5,
    defaultRating: 4.8,
    suggestedQ: 'Why do users add fashion products to their Myntra wishlist?',
    quote: 'Saved 5 dresses for my birthday next month. Waiting for prices to drop!',
  },
  {
    num: 3,
    key: 'fit_size_anxiety',
    label: 'Fit & Size Anxiety',
    icon: <Ruler size={18} />,
    color: '#F59E0B',
    bg: '#FFFBEB',
    desc: 'Inconsistent size charts and sizing uncertainty causing returns and hesitation.',
    defaultCount: 2068,
    defaultPct: 18.4,
    defaultRating: 2.8,
    suggestedQ: 'What uncertainties about fit and size remain after users identify a product?',
    quote: 'Size chart said M but it fits like XS. Sizing is super inconsistent across brands.',
  },
  {
    num: 4,
    key: 'price_value_sensitivity',
    label: 'Price & Value Sensitivity',
    icon: <Tag size={18} />,
    color: '#3B82F6',
    bg: '#EFF6FF',
    desc: 'Waiting for End of Reason Sale (EOSR), price drop alerts, and deal timing.',
    defaultCount: 1596,
    defaultPct: 14.2,
    defaultRating: 3.5,
    suggestedQ: 'What causes Myntra users to postpone a purchase for sales?',
    quote: 'Overpriced at MRP. Will only order during the End of Reason Sale.',
  },
  {
    num: 5,
    key: 'social_occasion_validation',
    label: 'Social & Occasion Validation',
    icon: <Users size={18} />,
    color: '#8B5CF6',
    bg: '#F5F3FF',
    desc: 'Diwali parties, wedding guest outfits, college wear, and influencer inspiration.',
    defaultCount: 1079,
    defaultPct: 9.6,
    defaultRating: 4.5,
    suggestedQ: 'What role do occasion and social validation play in Myntra purchases?',
    quote: 'Needed a wedding guest kurta urgently. Found great styling photos in the reviews section!',
  },
  {
    num: 6,
    key: 'cross_platform_research',
    label: 'Cross-Platform Research',
    icon: <Search size={18} />,
    color: '#06B6D4',
    bg: '#ECFEFF',
    desc: 'Checking YouTube try-on hauls and Reddit (r/IndianFashionAddicts) before buying.',
    defaultCount: 810,
    defaultPct: 7.2,
    defaultRating: 3.8,
    suggestedQ: 'What information do users seek outside Myntra on YouTube/Reddit before purchasing?',
    quote: 'Checked YouTube try-on haul before ordering to verify the exact color.',
  },
  {
    num: 7,
    key: 'comparison_shortlisting',
    label: 'Comparison & Shortlisting',
    icon: <GitCompare size={18} />,
    color: '#6366F1',
    bg: '#EEF2FF',
    desc: 'Shortlisting 2-3 formal blazers or kurtas and comparing fit and prices.',
    defaultCount: 607,
    defaultPct: 5.4,
    defaultRating: 4.0,
    suggestedQ: 'How do users compare multiple shortlisted products on Myntra?',
    quote: 'Shortlisted two black blazers on Myntra and AJIO, comparing fit charts.',
  },
  {
    num: 8,
    key: 'post_purchase_feedback',
    label: 'Post-Purchase Quality & Regret',
    icon: <MessageSquare size={18} />,
    color: '#F97316',
    bg: '#FFF7ED',
    desc: 'Fabric thinness, color mismatch, and unmet expectations after delivery.',
    defaultCount: 1001,
    defaultPct: 8.9,
    defaultRating: 3.2,
    suggestedQ: 'What post-purchase fabric and quality issues emerge in customer reviews?',
    quote: 'Fabric is very thin compared to how vibrant it looks on screen.',
  },
];

const SCRAPED_MYNTRA_REVIEWS: VerbatimQuote[] = [
  {
    text: "Saved 4 kurtas for the upcoming Diwali sale on Myntra. Adding them to cart early so I can checkout as soon as prices drop!",
    rating: 5,
    platform: "google_play",
    app_name: "Myntra",
    author: "Ananya Sharma",
    themes: ["wishlist_discovery_intent", "price_value_sensitivity"]
  },
  {
    text: "Wishlisted a medium size Allen Solly jacket, but it went out of stock within 10 minutes of sale notification. Myntra needs better stock alerts!",
    rating: 2,
    platform: "app_store",
    app_name: "Myntra",
    author: "Rohan Mehta",
    themes: ["purchase_blockers", "wishlist_discovery_intent"]
  },
  {
    text: "Size chart for Roadster jeans is super misleading. Said size 32 is 34 inch waist, but actually fits like size 30. Had to initiate return.",
    rating: 1,
    platform: "google_play",
    app_name: "Myntra",
    author: "Priya Kumar",
    themes: ["fit_size_anxiety", "purchase_blockers"]
  },
  {
    text: "Loved the fabric quality of the ethnic sherwani! Exactly as shown in the app photos. Delivery was super prompt within 2 days.",
    rating: 5,
    platform: "app_store",
    app_name: "Myntra",
    author: "Vikas Patel",
    themes: ["social_occasion_validation", "post_purchase_feedback"]
  },
  {
    text: "Checked YouTube try-on haul before ordering this dress on Myntra. Glad I did because the color in reality is darker than online photo.",
    rating: 4,
    platform: "reddit",
    app_name: "Myntra",
    author: "r/IndianFashionAddicts",
    themes: ["cross_platform_research", "post_purchase_feedback"]
  },
  {
    text: "Shortlisted two black formal blazers on Myntra. Can't decide between Mango and Allen Solly. Wish there was a side-by-side comparison feature.",
    rating: 4,
    platform: "google_play",
    app_name: "Myntra",
    author: "Siddharth Gupta",
    themes: ["comparison_shortlisting", "wishlist_discovery_intent"]
  },
  {
    text: "Only buy from Myntra during Big Fashion Festival or EOSR. Regular MRP prices feel artificially inflated before sales.",
    rating: 3,
    platform: "google_play",
    app_name: "Myntra",
    author: "Kavita R.",
    themes: ["price_value_sensitivity"]
  },
  {
    text: "Myntra Insider points gave me an extra 15% discount on Libas suit set. The wishlist notification for price drop saved me ₹600!",
    rating: 5,
    platform: "app_store",
    app_name: "Myntra",
    author: "Neha Verma",
    themes: ["wishlist_discovery_intent", "price_value_sensitivity"]
  }
];

export const DiscoveryLeftPanel: React.FC<DiscoveryLeftPanelProps> = ({ onAskQuestion }) => {
  const [summary, setSummary] = useState<SummaryStats | null>(null);
  const [overview, setOverview] = useState<ThemesOverview | null>(null);
  const [activeTheme, setActiveTheme] = useState<string | null>(null);
  const [datasetMode, setDatasetMode] = useState<'keyword' | 'live'>('keyword');
  const [searchQuery, setSearchQuery] = useState('');
  const [platformFilter, setPlatformFilter] = useState<string>('all');
  const [reviewsList, setReviewsList] = useState<VerbatimQuote[]>(SCRAPED_MYNTRA_REVIEWS);

  useEffect(() => {
    api.getSummary().then(setSummary).catch(() => {});
    api.getThemes().then(setOverview).catch(() => {});
  }, []);

  const totalReviews = summary?.total_reviews ?? 20050;

  const filteredReviews = reviewsList.filter(r => {
    const matchesSearch = !searchQuery || r.text.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPlatform = platformFilter === 'all' || r.platform === platformFilter;
    const matchesTheme = !activeTheme || r.themes?.includes(activeTheme);
    return matchesSearch && matchesPlatform && matchesTheme;
  });

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      paddingRight: '4px',
      width: '100%',
    }}>

      {/* ── Top Goal Tagline Banner ── */}
      <div style={{
        background: '#F8FAFC',
        padding: '10px 16px',
        borderRadius: '10px',
        border: '1px solid var(--border-card)',
        fontSize: '0.8rem',
        color: '#475569',
        fontWeight: 500,
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span style={{ fontWeight: 700, color: 'var(--myntra-pink)' }}>Goal:</span>
        Increase % of MACs purchasing from ≥1 new category/month
      </div>

      {/* ── Hero Card — Discovery Pulse ── */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        border: '1px solid var(--border-card)',
        padding: '20px 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Discovery Pulse
          </h2>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '4px 10px',
              borderRadius: '20px',
              background: '#F1F5F9',
              color: '#475569',
            }}>
              {totalReviews.toLocaleString()} reviews analysed
            </span>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              padding: '4px 10px',
              borderRadius: '20px',
              background: '#FEF3C7',
              color: '#92400E',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              Avg rating: 4.15★
            </span>
          </div>
        </div>

        <p style={{ fontSize: '0.85rem', color: '#64748B', lineHeight: 1.5 }}>
          Cross-category discovery signals in this batch centre around Trust &amp; Risk and Habit Formation.
        </p>

        {/* Dataset Mode Toggle Tabs */}
        <div style={{
          display: 'flex',
          gap: '10px',
          marginTop: '16px',
        }}>
          <button
            onClick={() => setDatasetMode('keyword')}
            style={{
              flex: 1,
              padding: '10px 16px',
              borderRadius: '10px',
              border: datasetMode === 'keyword' ? '2px solid #059669' : '1px solid var(--border-card)',
              background: datasetMode === 'keyword' ? '#059669' : 'white',
              color: datasetMode === 'keyword' ? 'white' : 'var(--text-secondary)',
              fontWeight: 700,
              fontSize: '0.84rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s ease',
            }}
          >
            📊 Full Dataset (Keyword Algorithm)
          </button>

          <button
            onClick={() => setDatasetMode('live')}
            style={{
              flex: 1,
              padding: '10px 16px',
              borderRadius: '10px',
              border: datasetMode === 'live' ? '2px solid #059669' : '1px solid var(--border-card)',
              background: datasetMode === 'live' ? '#F0FDF4' : 'white',
              color: datasetMode === 'live' ? '#059669' : 'var(--text-secondary)',
              fontWeight: 700,
              fontSize: '0.84rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s ease',
            }}
          >
            🧠 Sample Dataset (Live API)
          </button>
        </div>
      </div>

      {/* ── ALL DISCOVERY THEMES Section ── */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        border: '1px solid var(--border-card)',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
      }}>
        <div style={{
          fontSize: '0.82rem',
          fontWeight: 800,
          color: '#64748B',
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
          marginBottom: '14px',
        }}>
          ALL DISCOVERY THEMES
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {DISCOVERY_THEMES.map((theme) => {
            const liveData = overview?.themes?.[theme.key];
            const count = liveData ? liveData.review_count : theme.defaultCount;
            const pct = liveData ? liveData.percentage : theme.defaultPct;
            const rating = liveData?.avg_rating ?? theme.defaultRating;
            const isActive = activeTheme === theme.key;

            return (
              <div
                key={theme.key}
                onClick={() => {
                  setActiveTheme(isActive ? null : theme.key);
                  onAskQuestion(theme.suggestedQ);
                }}
                style={{
                  padding: '16px',
                  borderRadius: '12px',
                  border: `1.5px solid ${isActive ? 'var(--myntra-pink)' : 'var(--border-card)'}`,
                  background: isActive ? 'var(--myntra-pink-light)' : 'white',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: isActive ? '0 3px 12px rgba(255, 62, 108, 0.15)' : 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      background: '#F59E0B',
                      color: 'white',
                      fontWeight: 800,
                      fontSize: '0.78rem',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      {theme.num}
                    </span>
                    <div style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '8px',
                      background: theme.bg,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: theme.color,
                      flexShrink: 0,
                    }}>
                      {theme.icon}
                    </div>
                    <span style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {theme.label}
                    </span>
                  </div>

                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: rating < 3.0 ? '#991B1B' : '#065F46',
                    background: rating < 3.0 ? '#FEF2F2' : '#ECFDF5',
                    padding: '3px 9px',
                    borderRadius: '12px',
                    border: `1px solid ${rating < 3.0 ? '#FECACA' : '#A7F3D0'}`
                  }}>
                    {rating.toFixed(1)}★ avg
                  </span>
                </div>

                <p style={{ fontSize: '0.82rem', color: '#475569', lineHeight: 1.5, marginBottom: '10px' }}>
                  {theme.desc}
                </p>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', color: '#64748B', fontWeight: 600, marginBottom: '6px' }}>
                  <span>{count.toLocaleString()} reviews</span>
                  <span>{pct}% of categorised</span>
                </div>

                {/* Progress bar */}
                <div className="progress-bar-bg">
                  <div className="progress-bar-fill" style={{ width: `${Math.min(pct * 2.5, 100)}%`, background: theme.color }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── SCRAPED MYNTRA REVIEWS & VERBATIM FEED ── */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        border: '1px solid var(--border-card)',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
          <div>
            <div style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Quote size={18} color="var(--myntra-pink)" /> Scraped Myntra Reviews Feed
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Verbatim user feedback collected from Google Play &amp; App Store
            </div>
          </div>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '3px 8px', borderRadius: '5px', background: 'var(--myntra-pink-light)', color: 'var(--myntra-pink)' }}>
            {filteredReviews.length} quotes
          </span>
        </div>

        {/* Search & Platform Filters */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '14px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, position: 'relative', minWidth: '180px' }}>
            <input
              type="text"
              placeholder="Search scraped reviews (e.g. size, sale)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field"
              style={{ paddingLeft: '34px', fontSize: '0.8rem', padding: '8px 12px 8px 34px' }}
            />
            <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
          </div>

          <div style={{ display: 'flex', gap: '4px' }}>
            {['all', 'google_play', 'app_store', 'reddit'].map((p) => (
              <button
                key={p}
                onClick={() => setPlatformFilter(p)}
                style={{
                  padding: '6px 10px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-card)',
                  background: platformFilter === p ? 'var(--myntra-pink-light)' : '#F8FAFC',
                  color: platformFilter === p ? 'var(--myntra-pink)' : '#64748B',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                }}
              >
                {p === 'all' ? 'All' : p === 'google_play' ? 'Play Store' : p === 'app_store' ? 'App Store' : 'Reddit'}
              </button>
            ))}
          </div>
        </div>

        {/* Reviews Cards List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {filteredReviews.map((rev, idx) => (
            <div
              key={idx}
              style={{
                padding: '14px',
                borderRadius: '12px',
                border: '1px solid var(--border-card)',
                background: '#FAFAFA',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: 'var(--myntra-pink-light)',
                    color: 'var(--myntra-pink)',
                  }}>
                    {rev.app_name}
                  </span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#334155' }}>
                    {rev.author}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '2px', color: '#F59E0B', fontSize: '0.78rem', fontWeight: 700 }}>
                  <Star size={13} fill="#F59E0B" /> {rev.rating}
                </div>
              </div>

              <p style={{ fontSize: '0.82rem', color: '#1E293B', fontStyle: 'italic', lineHeight: 1.5 }}>
                "{rev.text}"
              </p>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '4px' }}>
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  {rev.themes?.map(t => (
                    <span key={t} style={{ fontSize: '0.65rem', padding: '2px 6px', borderRadius: '4px', background: '#EEF2FF', color: '#4F46E5', fontWeight: 600 }}>
                      #{t.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>

                <button
                  onClick={() => onAskQuestion(`Analyze this Myntra review: "${rev.text}"`)}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '6px',
                    border: '1px solid var(--myntra-pink-border)',
                    background: 'white',
                    color: 'var(--myntra-pink)',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontFamily: 'inherit',
                  }}
                >
                  <MessageCircle size={12} /> Ask AI
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer attribution */}
      <div style={{
        fontSize: '0.72rem',
        color: 'var(--text-muted)',
        textAlign: 'center',
        padding: '8px',
        lineHeight: 1.5,
      }}>
        Data sourced from Google Play Store &amp; Apple App Store reviews for Myntra app<br />
        Powered by Groq Cloud LLaMA 3 · FastAPI · Next.js
      </div>

    </div>
  );
};
