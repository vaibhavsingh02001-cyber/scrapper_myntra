import { NextRequest, NextResponse } from 'next/server';

const MYNTRA_QUOTES = [
  {
    text: "Saved 4 kurtas for the upcoming Diwali sale on Myntra. Adding them to cart early so I can checkout as soon as prices drop!",
    rating: 5, platform: "Play Store", app_name: "Myntra", author: "Ananya Sharma", themes: ["Wishlist Intent"]
  },
  {
    text: "Wishlisted a medium size Allen Solly jacket, but it went out of stock within 10 minutes of sale notification. Myntra needs better stock alerts!",
    rating: 2, platform: "App Store", app_name: "Myntra", author: "Rohan Mehta", themes: ["Purchase Blockers"]
  },
  {
    text: "Size chart for Roadster jeans is super misleading. Said size 32 is 34 inch waist, but actually fits like size 30. Had to initiate return.",
    rating: 1, platform: "Play Store", app_name: "Myntra", author: "Priya Kumar", themes: ["Fit & Size Anxiety"]
  },
  {
    text: "Loved the fabric quality of the ethnic sherwani! Exactly as shown in the app photos. Delivery was super prompt within 2 days.",
    rating: 5, platform: "App Store", app_name: "Myntra", author: "Vikas Patel", themes: ["Social & Occasion Validation"]
  },
  {
    text: "Checked YouTube try-on haul before ordering this dress on Myntra. Glad I did because the color in reality is darker than online photo.",
    rating: 4, platform: "Reddit", app_name: "Myntra", author: "r/IndianFashionAddicts", themes: ["Cross-Platform Research"]
  },
  {
    text: "Shortlisted two black formal blazers on Myntra. Can't decide between Mango and Allen Solly. Wish there was a side-by-side comparison feature.",
    rating: 4, platform: "Play Store", app_name: "Myntra", author: "Siddharth Gupta", themes: ["Comparison & Shortlisting"]
  }
];

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const theme = url.searchParams.get('theme') || 'all';
  const platform = url.searchParams.get('platform');
  const limit = parseInt(url.searchParams.get('limit') || '12', 10);

  let filtered = MYNTRA_QUOTES;
  if (platform && platform !== 'All') {
    filtered = filtered.filter(q => q.platform.toLowerCase() === platform.toLowerCase());
  }

  return NextResponse.json({
    theme,
    theme_label: 'Myntra Reviews',
    quotes: filtered.slice(0, limit),
    total_returned: filtered.length
  });
}
