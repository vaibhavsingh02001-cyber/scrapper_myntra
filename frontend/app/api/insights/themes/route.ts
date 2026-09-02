import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    total_reviews_analyzed: 20050,
    total_classified: 11240,
    total_unclassified: 8810,
    platform_breakdown: { google_play: 12500, app_store: 5200, reddit: 2350 },
    app_breakdown: { myntra: 20050 },
    themes: {
      wishlist_discovery_intent: {
        label: 'Habit Formation (Wishlist & Discovery Intent)',
        review_count: 3876,
        percentage: 34.5,
        avg_rating: 4.8,
        verbatim_quotes: [
          'Saved 5 dresses for my birthday next month. Waiting for prices to drop!',
          'My wishlist is basically my wardrobe wishlist — I have 140 items saved.'
        ]
      },
      purchase_blockers: {
        label: 'Trust & Risk (Purchase Blockers)',
        review_count: 2450,
        percentage: 21.8,
        avg_rating: 2.0,
        verbatim_quotes: [
          'Item went out of stock right while it was in my cart. So frustrating.'
        ]
      },
      fit_size_anxiety: {
        label: 'Fit & Size Anxiety',
        review_count: 2068,
        percentage: 18.4,
        avg_rating: 2.8,
        verbatim_quotes: [
          'Size chart for Roadster jeans is super misleading.'
        ]
      }
    },
    generated_at: new Date().toISOString()
  });
}
