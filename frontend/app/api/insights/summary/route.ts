import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    total_reviews: 20050,
    total_classified: 11240,
    app_breakdown: { myntra: 11240 },
    dominant_theme: 'wishlist_discovery_intent',
    dominant_theme_label: 'Habit Formation (Wishlist & Discovery Intent)',
    dominant_theme_count: 3876,
    top_5_themes: [
      { key: 'wishlist_discovery_intent', label: 'Habit Formation (Wishlist & Discovery Intent)', count: 3876, percentage: 34.5 },
      { key: 'purchase_blockers', label: 'Trust & Risk (Purchase Blockers)', count: 2450, percentage: 21.8 },
      { key: 'fit_size_anxiety', label: 'Fit & Size Anxiety', count: 2068, percentage: 18.4 },
      { key: 'price_value_sensitivity', label: 'Price & Value Sensitivity', count: 1596, percentage: 14.2 },
      { key: 'social_occasion_validation', label: 'Social & Occasion Validation', count: 1079, percentage: 9.6 }
    ],
    llm_sample_size: 20050,
    generated_at: new Date().toISOString()
  });
}
