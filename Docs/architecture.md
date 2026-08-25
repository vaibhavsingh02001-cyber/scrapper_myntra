# 🏗️ Architecture — Scapper

> **Project Name:** Scapper  
> **LLM Provider:** Groq (LLaMA 3 / Mixtral-8x7B via Groq Cloud API)  
> **Document Type:** Complete System Architecture  
> **Date:** August 2026  
> **Status:** In Development

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [System Layers](#2-system-layers)
3. [Component Deep-Dive](#3-component-deep-dive)
   - 3.1 [Frontend — Next.js Dashboard](#31-frontend--nextjs-dashboard)
   - 3.2 [Backend API — FastAPI](#32-backend-api--fastapi)
   - 3.3 [Scraping Engine](#33-scraping-engine)
   - 3.4 [LLM Extraction Pipeline — Groq](#34-llm-extraction-pipeline--groq)
   - 3.5 [Data Storage Layer](#35-data-storage-layer)
   - 3.6 [CLI Interface](#36-cli-interface)
4. [Data Flow](#4-data-flow)
5. [Request Lifecycle](#5-request-lifecycle)
6. [Directory Structure](#6-directory-structure)
7. [API Contract](#7-api-contract)
8. [Database Schema](#8-database-schema)
9. [LLM Prompt Architecture](#9-llm-prompt-architecture)
10. [Error Handling & Resilience](#10-error-handling--resilience)
11. [Security Considerations](#11-security-considerations)
12. [Deployment Architecture](#12-deployment-architecture)
13. [Technology Decision Matrix](#13-technology-decision-matrix)

---

## 1. Architecture Overview

Scapper follows a **modular, layered architecture** where each layer has a single, clearly defined responsibility. The system is divided into five primary tiers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT TIER                                  │
│         Next.js Dashboard  │  Python CLI  │  REST API Consumers     │
└───────────────────────┬─────────────┬───────────────────────────────┘
                        │             │
                        ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API TIER                                     │
│                    FastAPI (Python)                                 │
│          /scrape  │  /query  │  /jobs  │  /results  │  /export     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               ▼                    ▼                    ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   SCRAPING ENGINE    │  │  GROQ LLM LAYER  │  │  DATA STORE      │
│  Python + Playwright │  │  Extraction +    │  │  SQLite /        │
│  BeautifulSoup +     │  │  NL Querying     │  │  PostgreSQL +    │
│  Node.js Puppeteer   │  │  via Groq API    │  │  JSON / CSV      │
└──────────────────────┘  └──────────────────┘  └──────────────────┘
               │                    ▲
               └────────────────────┘
                  Raw HTML → Groq → Structured JSON
```

---

## 2. System Layers

| Layer | Responsibility | Technology |
|---|---|---|
| **Presentation** | User interaction, result display, search & query | Next.js 14 + React |
| **API Gateway** | Route requests, auth, rate limiting, orchestration | FastAPI (Python 3.11+) |
| **Scraping Engine** | Fetch & render web pages, extract raw HTML/text | Playwright, BeautifulSoup, Puppeteer |
| **LLM Pipeline** | Intelligent extraction, NL querying, summarization | Groq API (LLaMA 3 / Mixtral) |
| **Persistence** | Store jobs, results, schemas, and query history | SQLite (dev) / PostgreSQL (prod) |
| **CLI** | Headless, scriptable scraping for power users | Python (Click / Typer) |

---

## 3. Component Deep-Dive

### 3.1 Frontend — Next.js Dashboard

The frontend is a **Next.js 14 (App Router)** application providing:

- **Scrape Request Form** — URL input + natural language prompt field
- **Job Queue View** — Real-time status of active/completed scraping jobs
- **Results Explorer** — Paginated, searchable table of extracted data
- **Natural Language Query** — Chat-style interface to query scraped data via Groq
- **Export Controls** — Download results as JSON or CSV

#### Component Tree

```
app/
├── layout.tsx                  # Root layout, navigation, theme
├── page.tsx                    # Home / dashboard overview
├── scrape/
│   └── page.tsx                # Scrape submission form
├── jobs/
│   ├── page.tsx                # Job queue list
│   └── [jobId]/
│       └── page.tsx            # Job detail + result view
├── query/
│   └── page.tsx                # Natural language query interface
├── export/
│   └── page.tsx                # Export manager
└── components/
    ├── ScrapeForm.tsx
    ├── JobCard.tsx
    ├── ResultsTable.tsx
    ├── QueryChat.tsx
    └── ExportPanel.tsx
```

#### Frontend ↔ API Communication

```
Frontend (Next.js)
    │
    ├── POST /api/scrape        → Submit new scraping job
    ├── GET  /api/jobs          → List all jobs
    ├── GET  /api/jobs/{id}     → Get job status + result
    ├── POST /api/query         → Natural language query on results
    └── GET  /api/export/{id}   → Download JSON or CSV
```

---

### 3.2 Backend API — FastAPI

The FastAPI backend is the **central orchestrator** of the entire system. It:

- Receives scraping requests from the frontend/CLI
- Dispatches jobs to the Scraping Engine
- Sends extracted content to the Groq LLM Pipeline
- Persists results to the database
- Serves results back to clients

#### API Routers

```
fastapi_app/
├── main.py                     # App entrypoint, router registration
├── routers/
│   ├── scrape.py               # POST /scrape — submit job
│   ├── jobs.py                 # GET /jobs, GET /jobs/{id}
│   ├── query.py                # POST /query — NL query via Groq
│   ├── export.py               # GET /export/{id}?format=json|csv
│   └── health.py               # GET /health
├── services/
│   ├── scraper_service.py      # Orchestrates scraping engine
│   ├── groq_service.py         # Groq API calls (extraction + query)
│   ├── job_service.py          # Job CRUD, status management
│   └── export_service.py       # Data formatting (JSON/CSV)
├── models/
│   ├── job.py                  # Job SQLAlchemy model
│   ├── result.py               # Result model
│   └── schemas.py              # Pydantic request/response schemas
├── db/
│   ├── database.py             # DB connection, session factory
│   └── migrations/             # Alembic migrations
└── config.py                   # Environment config (Groq API key, etc.)
```

#### Background Task Processing

Scraping jobs run **asynchronously** using FastAPI's `BackgroundTasks` (or Celery for production):

```python
# Simplified flow
@router.post("/scrape")
async def submit_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    job = await job_service.create_job(request)
    background_tasks.add_task(scraper_service.run, job.id)
    return {"job_id": job.id, "status": "queued"}
```

---

### 3.3 Scraping Engine

The scraping engine handles **fetching and rendering** web pages. It has two modes:

#### Mode 1 — Static Pages (BeautifulSoup)
For pages that serve full HTML without JavaScript rendering:

```
URL
 │
 ▼
httpx / requests  →  Raw HTML
 │
 ▼
BeautifulSoup     →  Cleaned text / structured content
 │
 ▼
→ Groq LLM Pipeline
```

#### Mode 2 — Dynamic/JS-Heavy Pages (Playwright)
For Single-Page Applications (SPAs) or JS-rendered content:

```
URL
 │
 ▼
Playwright (Chromium headless)
 │  - Navigate to URL
 │  - Wait for JS to render (networkidle)
 │  - Scroll to trigger lazy loading
 │
 ▼
page.content()   →  Full rendered HTML
 │
 ▼
HTML Cleaner     →  Strip scripts, styles, comments
 │
 ▼
→ Groq LLM Pipeline
```

#### Supplementary — Node.js Puppeteer / Cheerio
For specific scenarios (e.g., sites blocking Python Playwright):

```
scraper_service.py
    └── calls → node_scraper/scraper.js (via subprocess)
                    └── Puppeteer fetches page
                    └── Cheerio parses structure
                    └── Returns JSON to Python
```

#### HTML Pre-processing Pipeline

Before sending to Groq, raw HTML goes through a cleaning pipeline to reduce token usage:

```
Raw HTML
    │
    ▼
1. Remove <script>, <style>, <noscript> tags
2. Remove HTML comments
3. Collapse whitespace
4. Extract visible text with structural hints
   (headings, lists, tables, paragraphs)
5. Truncate / chunk if > 6000 tokens
    │
    ▼
Cleaned Text Chunks → Groq LLM
```

---

### 3.4 LLM Extraction Pipeline — Groq

This is the **intelligence core** of Scapper. Groq is used for two distinct tasks:

#### Task A — Structured Data Extraction

Converts cleaned page text into structured JSON based on the user's prompt.

```
Input:
  - user_prompt: "Extract product name, price, rating, and description"
  - page_text: <cleaned HTML content>

Groq API Call:
  - Model: llama3-70b-8192 (or mixtral-8x7b-32768 for large pages)
  - Temperature: 0.1  (deterministic extraction)
  - Response format: JSON mode

Output:
  {
    "product_name": "...",
    "price": "...",
    "rating": "...",
    "description": "..."
  }
```

#### Task B — Natural Language Querying

Allows users to query previously scraped data using plain English.

```
Input:
  - user_query: "Which products have a rating above 4.5?"
  - stored_data: [array of extracted JSON objects]

Groq API Call:
  - Model: llama3-8b-8192  (faster, cheaper for query tasks)
  - System prompt: "You are a data analyst. Answer from the provided data only."

Output:
  Natural language answer with relevant data excerpts
```

#### Groq Service Architecture

```python
class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.extraction_model = "llama3-70b-8192"
        self.query_model = "llama3-8b-8192"

    async def extract(self, page_text: str, user_prompt: str) -> dict
    async def query(self, data: list[dict], user_query: str) -> str
    async def summarize(self, page_text: str) -> str
    def _chunk_text(self, text: str, max_tokens: int = 6000) -> list[str]
    def _build_extraction_prompt(self, text: str, prompt: str) -> list[dict]
    def _build_query_prompt(self, data: list, query: str) -> list[dict]
```

#### Prompt Strategy

```
SYSTEM:
  You are an expert web data extractor.
  Extract ONLY the fields requested by the user.
  Return a valid JSON object. Do not add extra fields.
  If a field is not found, set its value to null.

USER:
  Page Content:
  ---
  {cleaned_page_text}
  ---
  
  Extract the following: {user_prompt}
  
  Return as JSON.
```

---

### 3.5 Data Storage Layer

#### Development — SQLite

Simple, zero-config file-based database for local development.

#### Production — PostgreSQL

Scalable relational database for multi-user production deployment.

#### Schema Overview (see Section 8 for full schema)

```
jobs            → scraping job metadata (status, URL, prompt, timestamps)
results         → extracted JSON data linked to jobs
query_history   → NL queries and Groq responses
schemas         → inferred field schemas per domain
```

#### File Storage

- Raw HTML snapshots: `storage/raw/{job_id}.html`
- JSON exports: `storage/exports/{job_id}.json`
- CSV exports: `storage/exports/{job_id}.csv`

---

### 3.6 CLI Interface

A Python CLI (built with **Typer**) for headless/automated scraping:

```bash
# Basic scrape
scapper scrape --url "https://example.com" --prompt "Extract all product names and prices"

# Export result
scapper export --job-id abc123 --format csv --output ./results.csv

# Query stored data
scapper query --job-id abc123 "Which items cost more than $50?"

# List all jobs
scapper jobs list

# Batch scrape from file
scapper batch --file urls.txt --prompt "Extract title and author"
```

---

## 4. Data Flow

### Flow 1 — Scraping & Extraction

```
┌──────────┐    POST /scrape     ┌──────────┐
│  User /  │ ─────────────────► │  FastAPI │
│  Client  │                    │  Backend │
└──────────┘                    └────┬─────┘
                                     │ 1. Create Job (status: queued)
                                     │ 2. Dispatch Background Task
                                     ▼
                              ┌─────────────┐
                              │  Scraping   │
                              │  Engine     │
                              │ (Playwright │
                              │  / BS4)     │
                              └──────┬──────┘
                                     │ 3. Fetch & render page
                                     │ 4. Clean & chunk HTML
                                     ▼
                              ┌─────────────┐
                              │  Groq LLM   │
                              │  Pipeline   │
                              └──────┬──────┘
                                     │ 5. Extract structured JSON
                                     ▼
                              ┌─────────────┐
                              │  Database   │
                              │  (SQLite /  │
                              │  Postgres)  │
                              └──────┬──────┘
                                     │ 6. Store result (status: done)
                                     ▼
                              ┌──────────────┐
                              │  Client      │
                              │  polls GET   │
                              │  /jobs/{id}  │
                              └──────────────┘
```

### Flow 2 — Natural Language Query

```
┌──────────┐    POST /query      ┌──────────┐
│  User    │ ─────────────────► │  FastAPI │
│          │  {job_id, query}   └────┬─────┘
└──────────┘                        │ 1. Fetch stored results for job_id
                                     │ 2. Build NL query prompt
                                     ▼
                              ┌─────────────┐
                              │  Groq LLM   │
                              │  (query     │
                              │   model)    │
                              └──────┬──────┘
                                     │ 3. Generate natural language answer
                                     ▼
                              ┌──────────────┐
                              │  Client      │
                              │  receives    │
                              │  answer      │
                              └──────────────┘
```

---

## 5. Request Lifecycle

End-to-end lifecycle of a scraping request:

```
1. USER submits URL + prompt via Dashboard or CLI
        │
        ▼
2. FastAPI receives POST /scrape
   - Validates request (URL format, prompt not empty)
   - Creates Job record in DB with status = "queued"
   - Returns job_id immediately (async)
        │
        ▼
3. Background Task starts
   - Job status → "running"
   - Scraping Engine detects page type (static vs. JS)
        │
        ├── Static → BeautifulSoup fetch
        └── Dynamic → Playwright headless browser
        │
        ▼
4. HTML Cleaning & Chunking
   - Strip noise (scripts, styles, comments)
   - Reduce to visible, semantic content
   - Chunk if > token limit
        │
        ▼
5. Groq LLM Extraction (per chunk if needed)
   - Send system + user prompt + page content
   - Receive JSON response
   - Merge chunks if multiple
   - Validate JSON structure
        │
        ├── Success → continue
        └── Failure → retry with simplified prompt (max 3 retries)
        │
        ▼
6. Result Persistence
   - Save extracted JSON to DB
   - Generate JSON/CSV export files
   - Job status → "completed"
        │
        ▼
7. Client retrieves result via GET /jobs/{id}
   - Full extracted data returned
   - Available for NL querying and export
```

---

## 6. Directory Structure

```
scapper/
│
├── Docs/
│   ├── problem_statement.md
│   └── architecture.md              ← this file
│
├── backend/                         # FastAPI Python backend
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── routers/
│   │   ├── scrape.py
│   │   ├── jobs.py
│   │   ├── query.py
│   │   ├── export.py
│   │   └── health.py
│   ├── services/
│   │   ├── scraper_service.py
│   │   ├── groq_service.py
│   │   ├── job_service.py
│   │   └── export_service.py
│   ├── engines/
│   │   ├── playwright_engine.py     # JS page rendering
│   │   ├── bs4_engine.py            # Static page parsing
│   │   └── html_cleaner.py          # HTML pre-processing
│   ├── models/
│   │   ├── job.py
│   │   ├── result.py
│   │   └── schemas.py
│   ├── db/
│   │   ├── database.py
│   │   └── migrations/
│   └── storage/
│       ├── raw/                     # Raw HTML snapshots
│       └── exports/                 # JSON/CSV exports
│
├── node_scraper/                    # Node.js supplementary scraper
│   ├── package.json
│   ├── scraper.js                   # Puppeteer + Cheerio
│   └── utils/
│       └── cleaner.js
│
├── frontend/                        # Next.js dashboard
│   ├── package.json
│   ├── next.config.js
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── scrape/page.tsx
│   │   ├── jobs/
│   │   │   ├── page.tsx
│   │   │   └── [jobId]/page.tsx
│   │   ├── query/page.tsx
│   │   └── export/page.tsx
│   ├── components/
│   │   ├── ScrapeForm.tsx
│   │   ├── JobCard.tsx
│   │   ├── ResultsTable.tsx
│   │   ├── QueryChat.tsx
│   │   └── ExportPanel.tsx
│   └── lib/
│       └── api.ts                   # API client (fetch wrappers)
│
├── cli/                             # Python CLI tool
│   ├── __init__.py
│   ├── main.py                      # Typer CLI entrypoint
│   └── commands/
│       ├── scrape.py
│       ├── query.py
│       ├── export.py
│       └── jobs.py
│
├── .env.example                     # Environment variable template
├── docker-compose.yml               # Local dev orchestration
└── README.md
```

---

## 7. API Contract

### POST `/scrape` — Submit Scraping Job

**Request:**
```json
{
  "url": "https://example.com/products",
  "prompt": "Extract all product names, prices, and ratings",
  "mode": "auto",
  "options": {
    "wait_for_selector": ".product-card",
    "scroll": true,
    "max_pages": 1
  }
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "a1b2c3d4",
  "status": "queued",
  "created_at": "2026-08-24T15:00:00Z"
}
```

---

### GET `/jobs/{job_id}` — Get Job Status & Result

**Response (200 OK — Completed):**
```json
{
  "job_id": "a1b2c3d4",
  "status": "completed",
  "url": "https://example.com/products",
  "prompt": "Extract all product names, prices, and ratings",
  "created_at": "2026-08-24T15:00:00Z",
  "completed_at": "2026-08-24T15:00:07Z",
  "result": [
    {
      "product_name": "Widget Pro",
      "price": "$29.99",
      "rating": "4.8"
    }
  ],
  "result_count": 1,
  "export_urls": {
    "json": "/export/a1b2c3d4?format=json",
    "csv": "/export/a1b2c3d4?format=csv"
  }
}
```

---

### POST `/query` — Natural Language Query

**Request:**
```json
{
  "job_id": "a1b2c3d4",
  "query": "Which products cost less than $30 and have a rating above 4.5?"
}
```

**Response:**
```json
{
  "answer": "Based on the scraped data, 2 products match: Widget Pro ($29.99, 4.8★) and Basic Gadget ($19.99, 4.7★).",
  "relevant_records": [
    { "product_name": "Widget Pro", "price": "$29.99", "rating": "4.8" },
    { "product_name": "Basic Gadget", "price": "$19.99", "rating": "4.7" }
  ]
}
```

---

### GET `/export/{job_id}` — Download Results

**Query Params:** `?format=json` or `?format=csv`

**Response:** File download (Content-Disposition: attachment)

---

### GET `/health` — Health Check

```json
{
  "status": "ok",
  "groq_api": "reachable",
  "database": "connected"
}
```

---

## 8. Database Schema

### Table: `jobs`

| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique job identifier |
| `url` | TEXT | Target URL to scrape |
| `prompt` | TEXT | User's extraction prompt |
| `mode` | TEXT | `auto`, `static`, `dynamic` |
| `status` | TEXT | `queued`, `running`, `completed`, `failed` |
| `error_message` | TEXT | Error details if failed |
| `scrape_mode_used` | TEXT | `playwright` or `beautifulsoup` |
| `groq_model_used` | TEXT | Model name used for extraction |
| `token_usage` | INTEGER | Groq tokens consumed |
| `created_at` | TIMESTAMP | Job creation time |
| `completed_at` | TIMESTAMP | Job completion time |

---

### Table: `results`

| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique result identifier |
| `job_id` | UUID (FK → jobs) | Parent job |
| `data` | JSONB | Extracted structured data |
| `raw_html_path` | TEXT | Path to raw HTML snapshot |
| `record_count` | INTEGER | Number of extracted records |
| `created_at` | TIMESTAMP | Result creation time |

---

### Table: `query_history`

| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Query record ID |
| `job_id` | UUID (FK → jobs) | Related scraping job |
| `user_query` | TEXT | User's natural language question |
| `groq_answer` | TEXT | Groq's response |
| `model_used` | TEXT | Groq model used |
| `token_usage` | INTEGER | Tokens consumed |
| `created_at` | TIMESTAMP | Query timestamp |

---

## 9. LLM Prompt Architecture

### Extraction Prompt Template

```
[SYSTEM]
You are an expert web data extraction assistant.
Your task is to extract structured data from the provided web page content.

Rules:
- Extract ONLY the fields specified by the user.
- Return a JSON array of objects if there are multiple records, or a single JSON object if there is one.
- If a field cannot be found on the page, set its value to null.
- Do NOT infer or hallucinate data not present on the page.
- Do NOT include markdown formatting, only return raw JSON.

[USER]
Web Page Content:
```
{cleaned_page_text}
```

Extract the following information:
{user_prompt}

Return valid JSON only.
```

### Query Prompt Template

```
[SYSTEM]
You are a data analyst. You have access to the following scraped dataset.
Answer the user's question accurately and concisely based ONLY on this data.
If the answer cannot be determined from the data, say so explicitly.

Dataset:
```json
{stored_data_json}
```

[USER]
{user_query}
```

### Model Selection Logic

| Use Case | Model | Reason |
|---|---|---|
| Extraction (short pages) | `llama3-8b-8192` | Fast, low-cost, sufficient |
| Extraction (long pages) | `mixtral-8x7b-32768` | 32K context window |
| Extraction (complex/nested) | `llama3-70b-8192` | Best comprehension |
| NL Querying | `llama3-8b-8192` | Speed priority for chat |
| Summarization | `llama3-8b-8192` | Efficient for summaries |

---

## 10. Error Handling & Resilience

### Scraping Errors

| Error | Strategy |
|---|---|
| Connection timeout | Retry up to 3x with exponential backoff |
| CAPTCHA / bot block | Log, mark job as `blocked`, notify user |
| JS render timeout | Fall back to static BeautifulSoup parse |
| Empty page content | Mark as `failed` with descriptive error |

### LLM Errors

| Error | Strategy |
|---|---|
| Groq rate limit (429) | Queue and retry with exponential backoff |
| Invalid JSON response | Retry with stricter JSON-mode prompt |
| Context window exceeded | Chunk content and merge results |
| Empty or null extraction | Retry with simplified prompt (max 3x) |

### Retry Policy

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(GroqRateLimitError)
)
async def call_groq_with_retry(prompt):
    ...
```

---

## 11. Security Considerations

| Concern | Mitigation |
|---|---|
| **Groq API Key exposure** | Stored in `.env`, never committed to git |
| **SSRF via URL injection** | Validate & allowlist URL schemes (http/https only) |
| **Prompt injection via page content** | Sanitize page text; system prompt enforces rules |
| **Data privacy** | No PII stored beyond what's in scraped content |
| **robots.txt compliance** | Check and honor robots.txt before every scrape |
| **Rate limiting API** | Implement per-IP rate limiting on FastAPI endpoints |
| **CORS** | Restrict CORS origins to the frontend domain |

---

## 12. Deployment Architecture

### Local Development

```
docker-compose up
    │
    ├── backend   → FastAPI on :8000
    ├── frontend  → Next.js on :3000
    └── db        → PostgreSQL on :5432
```

### Production (Recommended)

```
                    ┌─────────────────┐
                    │   Cloudflare /  │
                    │   Nginx Proxy   │
                    └────────┬────────┘
                             │
               ┌─────────────┴─────────────┐
               ▼                           ▼
     ┌─────────────────┐        ┌─────────────────┐
     │   Next.js App   │        │   FastAPI App   │
     │ (Vercel / VPS)  │        │  (Docker / VPS) │
     └─────────────────┘        └────────┬────────┘
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                    ┌──────────────────┐   ┌──────────────────┐
                    │   PostgreSQL     │   │   Groq Cloud API │
                    │  (Managed DB)    │   │  (External LLM)  │
                    └──────────────────┘   └──────────────────┘
```

### Environment Variables

```ini
# .env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_EXTRACTION_MODEL=llama3-70b-8192
GROQ_QUERY_MODEL=llama3-8b-8192

DATABASE_URL=postgresql://user:pass@localhost:5432/scapper
STORAGE_PATH=./backend/storage

NEXT_PUBLIC_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000

MAX_RETRIES=3
REQUEST_TIMEOUT=30
MAX_TOKENS_PER_CHUNK=6000
```

---

## 13. Technology Decision Matrix

| Decision | Choice | Alternatives Considered | Rationale |
|---|---|---|---|
| LLM Provider | **Groq** | OpenAI, Anthropic, Ollama | LPU speed + cost + free tier |
| LLM Model | **LLaMA 3 / Mixtral** | GPT-4o, Claude 3 | Open weights, large context |
| Backend Framework | **FastAPI** | Django, Flask, Express | Async-native, auto OpenAPI docs |
| Frontend Framework | **Next.js 14** | React SPA, Svelte, Vue | SSR, App Router, ecosystem |
| Scraping (dynamic) | **Playwright** | Selenium, Puppeteer | Python-native, fast, modern |
| Scraping (static) | **BeautifulSoup** | lxml, Scrapy | Simple, lightweight |
| Database (dev) | **SQLite** | MySQL | Zero config, file-based |
| Database (prod) | **PostgreSQL** | MySQL, MongoDB | JSONB support, reliability |
| CLI | **Typer** | Click, argparse | Type hints, auto help text |

---

*This architecture document is a living reference and will be updated as the project evolves through each development phase.*
