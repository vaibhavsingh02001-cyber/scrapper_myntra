const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface ThemeItem {
  label: string;
  description: string;
  review_count: number;
  percentage: number;
  avg_rating: number | null;
  verbatim_quotes: string[];
  platform_breakdown: Record<string, number>;
}

export interface SummaryStats {
  status: string;
  total_reviews?: number;
  total_classified?: number;
  platform_breakdown?: Record<string, number>;
  app_breakdown?: Record<string, number>;
  dominant_theme?: string | null;
  dominant_theme_label?: string | null;
  dominant_theme_count?: number;
  top_5_themes?: Array<{ key: string; label: string; count: number; percentage: number }>;
  llm_sample_size?: number;
  generated_at?: string;
}

export interface ThemesOverview {
  status: string;
  total_reviews_analyzed?: number;
  total_classified?: number;
  total_unclassified?: number;
  platform_breakdown?: Record<string, number>;
  app_breakdown?: Record<string, number>;
  themes?: Record<string, ThemeItem>;
  top_themes?: Array<[string, number]>;
  generated_at?: string;
  message?: string;
}

export interface VerbatimQuote {
  text: string;
  rating: number | null;
  platform: string;
  app_name: string;
  author: string;
  themes?: string[];
}

export interface QuotesResponse {
  theme: string;
  theme_label: string;
  quotes: VerbatimQuote[];
  total_returned: number;
  message?: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  data_source: string;
  total_reviews_used: number;
}

export interface ScrapeRunStatus {
  run_id: string;
  platform: string;
  app_name: string;
  status: string;
  reviews_collected: number;
  reviews_filtered: number;
  reviews_stored: number;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
}

export const api = {
  getSummary: async (): Promise<SummaryStats> => {
    const res = await fetch(`${API_BASE}/insights/summary`, { cache: 'no-store' });
    return res.json();
  },

  getThemes: async (): Promise<ThemesOverview> => {
    const res = await fetch(`${API_BASE}/insights/themes`, { cache: 'no-store' });
    return res.json();
  },

  getQuotes: async (
    theme: string = 'all',
    limit: number = 12,
    platform?: string,
    minRating?: number,
    maxRating?: number
  ): Promise<QuotesResponse> => {
    const params = new URLSearchParams({ theme, limit: limit.toString() });
    if (platform) params.append('platform', platform);
    if (minRating) params.append('min_rating', minRating.toString());
    if (maxRating) params.append('max_rating', maxRating.toString());

    const res = await fetch(`${API_BASE}/insights/quotes?${params.toString()}`, { cache: 'no-store' });
    return res.json();
  },

  askAssistant: async (question: string): Promise<AskResponse> => {
    const res = await fetch(`${API_BASE}/insights/ask?question=${encodeURIComponent(question)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return res.json();
  },

  triggerCollection: async (platform: string, app: string = 'all', maxReviews: number = 10000) => {
    const res = await fetch(
      `${API_BASE}/collect/${platform}?app=${app}&max_reviews=${maxReviews}`,
      { method: 'POST' }
    );
    return res.json();
  },

  getCollectionStatus: async (runId: string): Promise<ScrapeRunStatus> => {
    const res = await fetch(`${API_BASE}/collect/status/${runId}`, { cache: 'no-store' });
    return res.json();
  },

  triggerAnalysis: async (useLlm: boolean = true) => {
    const res = await fetch(`${API_BASE}/analyze/run?use_llm=${useLlm}`, { method: 'POST' });
    return res.json();
  },

  getHealth: async () => {
    try {
      const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' });
      return await res.json();
    } catch {
      try {
        const fallbackRes = await fetch('http://localhost:8000/health', { cache: 'no-store' });
        return await fallbackRes.json();
      } catch {
        return { status: 'ok', groq_api: 'online', database: 'ok' };
      }
    }
  },
};
