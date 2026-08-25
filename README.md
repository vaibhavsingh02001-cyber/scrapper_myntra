# 🚀 Scapper & Myntra AI Discovery Engine

> **Intelligent LLM-Powered Web Scraping Platform & Myntra Wishlist Behavioral Research Engine**  
> **LLM Provider:** Groq Cloud API (LLaMA 3 70B & Mixtral LPUs)  
> **Tech Stack:** Python 3.11, FastAPI, Next.js 16 (App Router), Typer CLI, SQLite/PostgreSQL, Playwright, BeautifulSoup4, VADER

---

## 📌 Overview

**Scapper** is an end-to-end intelligent web scraping and consumer behavior discovery platform. It combines:

1. **Generic Web Scraping Engine**: Accepts any URL and plain-English prompt to extract structured JSON data using BeautifulSoup, Playwright (dynamic SPAs), and Groq LPUs.
2. **Myntra AI Discovery Engine**: Scrapes, noise-filters, and classifies user feedback across a **Structured 5-Dimension Research Taxonomy** to answer key research questions about wishlist-to-purchase behavior with quantified, evidence-backed output.

---

## 🌟 Key Features

### 🛍️ Myntra Discovery Engine Features
- **Data Collection**: Live scrapers for Google Play Store (`com.myntra.android`), Apple App Store (`Myntra`), and Reddit (`r/IndianFashionAddicts`, `r/IndianSkincareAddicts`, `r/india`, `r/femalefashionadvice`).
- **Relevance & Noise Filter**: Pre-LLM keyword relevance seeding ("wishlist", "still deciding", "size chart", "returned it", "saved for later", "waiting for price drop"), PII redaction, emoji-only drops, deduplication.
- **Structured 5-Dimension Research Taxonomy**:
  - `wishlist_trigger`: price_wait / styling_inspiration / bookmark_later / gifting / comparison_shopping
  - `purchase_blocker`: fit_size_uncertainty / price_timing / trust_reviews_photos / occasion_mismatch / styling_doubt / competitor_comparison / needs_social_validation
  - `intent_strength`: explicit_intent / vague_passive
  - `comparison_behavior`: cross_platform_price / cross_brand / seeking_outside_opinion
  - `segment_cue`: first_time_buyer / repeat_shopper / budget_conscious / occasion_driven
- **Structured LLM JSON Classification**: Groq LLaMA 3 70B classifies reviews into structured JSON with paraphrased reasons.
- **Quantification Engine**: Frequency %, VADER sentiment polarity, co-occurrence matrix, and time trends.
- **Ranked Opportunity Map Deliverable**: Ranked friction themes sorted by severity score and potential impact on wishlist-to-purchase conversion.
- **10 Core Research Questions API**: Empirical data answers mapped directly to core user research questions.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 DATA COLLECTION LAYER                       │
│  Google Play → Myntra App Reviews                           │
│  Apple App Store → Myntra iOS Reviews                       │
│  Reddit → r/IndianFashionAddicts, r/femalefashionadvice     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             RELEVANCE & NOISE FILTERING LAYER               │
│  – Keyword relevance filter (wishlist, size, price drop)    │
│  – PII Redaction (phone, email, cards)                      │
│  – Low-quality review drops (< 30 chars, emoji-only)        │
│  – Hash-based deduplication                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          STRUCTURED 5-DIMENSION TAXONOMY LAYER              │
│  Regex Engine + Groq LLaMA 3 70B Structured JSON Classifier │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│       QUANTIFICATION ENGINE & OPPORTUNITY MAP API           │
│  GET /research/questions     POST /collect/{platform}       │
│  GET /report/opportunity-map POST /analyze/run              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          DISCOVERY PULSE DASHBOARD (Next.js)                │
│  – Ranked Opportunity Map Report                            │
│  – 10 Grounded Research Questions View                      │
│  – 5-Dimension Taxonomy Map                                 │
│  – Verbatim Review Quotes & Paraphrased Evidence            │
│  – Live Scraper & Pipeline Terminal Control                 │
│  – Groq Grounded AI Insights Assistant                      │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Clone & Configure Environment

```bash
git clone https://github.com/your-username/scapper.git
cd scapper

# Create .env from template
cp .env.example .env
```

Edit `.env` and set your Groq API key:
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 2. Run with Docker Compose (Recommended)

```bash
docker-compose up --build
```
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Local Development Setup

### Backend (Python)

```bash
# Create virtualenv
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations
python -m backend.db.init_db

# Run FastAPI dev server
uvicorn backend.main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 🛠️ CLI Usage

```bash
# 1. View all CLI commands
python -m cli.main --help

# 2. Trigger review collection
python -m cli.main discovery collect --platform google_play --app myntra --max-reviews 5000

# 3. Run Dual-Engine classification
python -m cli.main discovery analyze

# 4. View dataset summary
python -m cli.main discovery summary

# 5. Ask Groq Insights Assistant
python -m cli.main discovery ask "Why do users add items to wishlists without buying?"
```

---

## 🧪 Testing

```bash
# Run full pytest suite (36 tests)
python -m pytest backend/tests/ -v

# Run frontend build check
cd frontend && npm run build
```

---

## 📄 Documentation

- [Problem Statement](Docs/problem_statement.md)
- [Architecture & Design](Docs/architecture.md)
- [Phase-wise Implementation Guide](Docs/implementation.md)
