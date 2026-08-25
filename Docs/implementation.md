# 🚀 Phase-wise Implementation Plan — Scapper

> **Project Name:** Scapper  
> **LLM Provider:** Groq (LLaMA 3 / Mixtral via Groq Cloud API)  
> **Document Type:** Phase-wise Implementation Guide  
> **Reference:** [architecture.md](./architecture.md) | [problem_statement.md](./problem_statement.md)  
> **Date:** August 2026  
> **Total Duration:** 10 Weeks

---

## Table of Contents

1. [Implementation Overview](#1-implementation-overview)
2. [Phase 0 — Environment Setup & Project Scaffolding](#2-phase-0--environment-setup--project-scaffolding)
3. [Phase 1 — Database Layer & Core Models](#3-phase-1--database-layer--core-models)
4. [Phase 2 — Scraping Engine](#4-phase-2--scraping-engine)
5. [Phase 3 — Groq LLM Integration](#5-phase-3--groq-llm-integration)
6. [Phase 4 — FastAPI Backend & REST API](#6-phase-4--fastapi-backend--rest-api)
7. [Phase 5 — Next.js Frontend Dashboard](#7-phase-5--nextjs-frontend-dashboard)
8. [Phase 6 — CLI Tool](#8-phase-6--cli-tool)
9. [Phase 7 — Error Handling, Retry & Resilience](#9-phase-7--error-handling-retry--resilience)
10. [Phase 8 — Testing & Quality Assurance](#10-phase-8--testing--quality-assurance)
11. [Phase 9 — Dockerization & Deployment](#11-phase-9--dockerization--deployment)
12. [Phase 10 — Polish, Docs & Final Review](#12-phase-10--polish-docs--final-review)
13. [Dependency Graph](#13-dependency-graph)
14. [Progress Tracker](#14-progress-tracker)

---

## 1. Implementation Overview

The project is divided into **10 sequential phases** ordered by dependency — foundational infrastructure is built first, followed by core logic layers, then the user-facing interfaces, and finally testing and deployment.

```
Phase 0  ─── Environment & Scaffolding
    │
    ▼
Phase 1  ─── Database Layer & Core Models
    │
    ▼
Phase 2  ─── Scraping Engine (BS4 + Playwright + Node.js)
    │
    ▼
Phase 3  ─── Groq LLM Integration (Extraction + Query)
    │
    ▼
Phase 4  ─── FastAPI Backend & REST API
    │
    ▼
Phase 5  ─── Next.js Frontend Dashboard
    │
    ▼
Phase 6  ─── CLI Tool (Typer)
    │
    ▼
Phase 7  ─── Error Handling & Resilience
    │
    ▼
Phase 8  ─── Testing & QA
    │
    ▼
Phase 9  ─── Dockerization & Deployment
    │
    ▼
Phase 10 ─── Polish, Documentation & Final Review
```

| Phase | Name | Duration | Priority |
|---|---|---|---|
| **0** | Environment Setup & Project Scaffolding | Day 1–2 | Critical |
| **1** | Database Layer & Core Models | Day 3–4 | Critical |
| **2** | Scraping Engine | Week 1–2 | Critical |
| **3** | Groq LLM Integration | Week 2–3 | Critical |
| **4** | FastAPI Backend & REST API | Week 3–4 | Critical |
| **5** | Next.js Frontend Dashboard | Week 5–6 | High |
| **6** | CLI Tool | Week 6 | Medium |
| **7** | Error Handling & Resilience | Week 7 | High |
| **8** | Testing & QA | Week 8 | High |
| **9** | Dockerization & Deployment | Week 9 | High |
| **10** | Polish, Docs & Final Review | Week 10 | Medium |

---

## 2. Phase 0 — Environment Setup & Project Scaffolding

> **Duration:** Day 1–2  
> **Goal:** Set up the full monorepo structure, install all dependencies, configure environment variables, and verify all tools are working.

### 2.1 Repository & Directory Setup

Create the monorepo folder structure as defined in `architecture.md § 6`:

```bash
mkdir -p scapper/{backend/{routers,services,engines,models,db,storage/{raw,exports}},frontend,node_scraper/utils,cli/commands,Docs}
```

**Final directory structure to verify:**
```
scapper/
├── backend/
├── frontend/
├── node_scraper/
├── cli/
├── Docs/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

### 2.2 Python Backend Environment

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# Install core dependencies
pip install fastapi uvicorn[standard] sqlalchemy alembic
pip install httpx playwright beautifulsoup4 lxml
pip install groq tenacity python-dotenv pydantic
pip install typer rich pandas

# Install Playwright browsers
playwright install chromium
```

**`backend/requirements.txt`:**
```
fastapi==0.111.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.30
alembic==1.13.1
httpx==0.27.0
playwright==1.44.0
beautifulsoup4==4.12.3
lxml==5.2.2
groq==0.9.0
tenacity==8.3.0
python-dotenv==1.0.1
pydantic==2.7.1
pandas==2.2.2
aiofiles==23.2.1
```

### 2.3 Node.js Scraper Environment

```bash
cd node_scraper
npm init -y
npm install puppeteer cheerio axios
```

**`node_scraper/package.json`:**
```json
{
  "name": "scapper-node-scraper",
  "version": "1.0.0",
  "dependencies": {
    "puppeteer": "^22.0.0",
    "cheerio": "^1.0.0",
    "axios": "^1.7.0"
  }
}
```

### 2.4 Next.js Frontend Setup

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
npm install axios react-query lucide-react
```

### 2.5 Environment Variables

Create `.env.example` at the project root:

```ini
# Groq LLM
GROQ_API_KEY=gsk_your_key_here
GROQ_EXTRACTION_MODEL=llama3-70b-8192
GROQ_QUERY_MODEL=llama3-8b-8192

# Database
DATABASE_URL=sqlite:///./scapper.db
# For production:
# DATABASE_URL=postgresql://user:pass@localhost:5432/scapper

# Storage
STORAGE_PATH=./backend/storage

# API
NEXT_PUBLIC_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000

# Scraper config
MAX_RETRIES=3
REQUEST_TIMEOUT=30
MAX_TOKENS_PER_CHUNK=6000
```

Copy to `.env` and fill in the Groq API key.

### 2.6 Git Setup

```bash
git init
echo ".env" >> .gitignore
echo ".venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "node_modules/" >> .gitignore
echo ".next/" >> .gitignore
echo "backend/storage/raw/*" >> .gitignore
echo "backend/storage/exports/*" >> .gitignore
git add .
git commit -m "chore: initial project scaffolding"
```

### ✅ Phase 0 Exit Criteria
- [ ] All directories created as per architecture
- [ ] Python venv active, all packages install without errors
- [ ] `playwright install chromium` succeeds
- [ ] Node.js packages installed in `node_scraper/`
- [ ] Next.js dev server runs (`npm run dev` → `localhost:3000`)
- [ ] `.env` created with valid Groq API key
- [ ] `.gitignore` excludes secrets and build artifacts

---

## 3. Phase 1 — Database Layer & Core Models

> **Duration:** Day 3–4  
> **Goal:** Set up SQLAlchemy ORM models, Alembic migrations, and the DB session factory. Everything that touches the DB in later phases depends on this.

### 3.1 Database Connection (`backend/db/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite only
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3.2 SQLAlchemy Models

**`backend/models/job.py`** — Jobs table (ref: `architecture.md § 8`):

```python
import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from backend.db.database import Base
from datetime import datetime

class Job(Base):
    __tablename__ = "jobs"

    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url            = Column(Text, nullable=False)
    prompt         = Column(Text, nullable=False)
    mode           = Column(String, default="auto")       # auto | static | dynamic
    status         = Column(String, default="queued")     # queued | running | completed | failed | blocked
    error_message  = Column(Text, nullable=True)
    scrape_mode_used = Column(String, nullable=True)      # playwright | beautifulsoup
    groq_model_used  = Column(String, nullable=True)
    token_usage    = Column(Integer, default=0)
    created_at     = Column(DateTime, default=datetime.utcnow)
    completed_at   = Column(DateTime, nullable=True)
```

**`backend/models/result.py`** — Results table:

```python
import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.database import Base
from datetime import datetime

class Result(Base):
    __tablename__ = "results"

    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id        = Column(String, ForeignKey("jobs.id"), nullable=False)
    data          = Column(Text, nullable=True)        # JSON string
    raw_html_path = Column(Text, nullable=True)
    record_count  = Column(Integer, default=0)
    created_at    = Column(DateTime, default=datetime.utcnow)
```

**`backend/models/query_history.py`** — Query History table:

```python
class QueryHistory(Base):
    __tablename__ = "query_history"

    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id      = Column(String, ForeignKey("jobs.id"), nullable=False)
    user_query  = Column(Text, nullable=False)
    groq_answer = Column(Text, nullable=True)
    model_used  = Column(String, nullable=True)
    token_usage = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)
```

### 3.3 Pydantic Schemas (`backend/models/schemas.py`)

```python
from pydantic import BaseModel, HttpUrl
from typing import Optional, Any, List
from datetime import datetime

class ScrapeRequest(BaseModel):
    url: HttpUrl
    prompt: str
    mode: str = "auto"   # auto | static | dynamic

class JobResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime

class JobDetailResponse(BaseModel):
    job_id: str
    status: str
    url: str
    prompt: str
    created_at: datetime
    completed_at: Optional[datetime]
    result: Optional[Any]
    result_count: Optional[int]
    error_message: Optional[str]

class QueryRequest(BaseModel):
    job_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str
    relevant_records: Optional[List[dict]]
```

### 3.4 Alembic Migration Setup

```bash
cd backend
alembic init db/migrations
# Edit alembic.ini: sqlalchemy.url = sqlite:///./scapper.db
# Edit db/migrations/env.py: import models; target_metadata = Base.metadata
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
```

### 3.5 Config (`backend/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_EXTRACTION_MODEL: str = "llama3-70b-8192"
    GROQ_QUERY_MODEL: str = "llama3-8b-8192"
    DATABASE_URL: str = "sqlite:///./scapper.db"
    STORAGE_PATH: str = "./backend/storage"
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    MAX_TOKENS_PER_CHUNK: int = 6000
    CORS_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
```

### ✅ Phase 1 Exit Criteria
- [ ] `jobs`, `results`, `query_history` tables created via Alembic migration
- [ ] `get_db()` dependency injection works in FastAPI
- [ ] All Pydantic schemas validate correctly
- [ ] `backend/config.py` reads `.env` without errors

---

## 4. Phase 2 — Scraping Engine

> **Duration:** Week 1–2  
> **Goal:** Build the full scraping engine: static (BeautifulSoup), dynamic (Playwright), HTML cleaning pipeline, and the Node.js fallback scraper.

### 4.1 HTML Cleaner (`backend/engines/html_cleaner.py`)

First, build the shared HTML pre-processing module used by all scraping modes:

```python
from bs4 import BeautifulSoup
import re

class HTMLCleaner:
    """Strips noise from raw HTML and returns clean visible text."""

    def clean(self, raw_html: str) -> str:
        soup = BeautifulSoup(raw_html, "lxml")
        # Step 1: Remove script, style, noscript, meta, head
        for tag in soup(["script", "style", "noscript", "meta", "head", "footer", "nav"]):
            tag.decompose()
        # Step 2: Remove HTML comments
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()
        # Step 3: Get visible text preserving structure
        text = soup.get_text(separator="\n", strip=True)
        # Step 4: Collapse excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def chunk(self, text: str, max_chars: int = 12000) -> list[str]:
        """Split text into chunks below the token limit."""
        chunks = []
        while len(text) > max_chars:
            split_at = text.rfind('\n', 0, max_chars)
            if split_at == -1:
                split_at = max_chars
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip()
        if text:
            chunks.append(text)
        return chunks
```

### 4.2 Static Scraper (`backend/engines/bs4_engine.py`)

For static HTML pages (no JS rendering needed):

```python
import httpx
from backend.engines.html_cleaner import HTMLCleaner
from backend.config import settings

class BS4Engine:
    def __init__(self):
        self.cleaner = HTMLCleaner()

    async def fetch(self, url: str) -> tuple[str, str]:
        """Returns (raw_html, cleaned_text)"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            raw_html = response.text
            cleaned = self.cleaner.clean(raw_html)
            return raw_html, cleaned
```

### 4.3 Playwright Engine (`backend/engines/playwright_engine.py`)

For JavaScript-rendered / dynamic pages (SPAs):

```python
from playwright.async_api import async_playwright
from backend.engines.html_cleaner import HTMLCleaner
from backend.config import settings

class PlaywrightEngine:
    def __init__(self):
        self.cleaner = HTMLCleaner()

    async def fetch(self, url: str, wait_for_selector: str = None) -> tuple[str, str]:
        """Launches headless Chromium, renders the page, returns (raw_html, cleaned_text)"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=settings.REQUEST_TIMEOUT * 1000)

            # Scroll to trigger lazy loading
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1500)

            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=10000)

            raw_html = await page.content()
            await browser.close()

            cleaned = self.cleaner.clean(raw_html)
            return raw_html, cleaned
```

### 4.4 Page Type Detector

Auto-detect whether to use BS4 or Playwright:

```python
# backend/engines/detector.py

KNOWN_SPA_DOMAINS = ["react", "angular", "vue", "next"]

async def detect_mode(url: str, mode: str = "auto") -> str:
    """Returns 'playwright' or 'beautifulsoup'"""
    if mode == "static":
        return "beautifulsoup"
    if mode == "dynamic":
        return "playwright"
    # Try static fetch first; if content is minimal → switch to Playwright
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(url, follow_redirects=True)
            # Heuristic: if body is short and has noscript tags → JS-rendered
            if len(r.text) < 2000 or "<noscript>" in r.text.lower():
                return "playwright"
        except Exception:
            pass
    return "beautifulsoup"
```

### 4.5 Scraper Service Orchestrator (`backend/services/scraper_service.py`)

```python
import os, json, aiofiles
from backend.engines.bs4_engine import BS4Engine
from backend.engines.playwright_engine import PlaywrightEngine
from backend.engines.detector import detect_mode
from backend.config import settings

class ScraperService:
    def __init__(self):
        self.bs4 = BS4Engine()
        self.playwright = PlaywrightEngine()

    async def scrape(self, url: str, mode: str = "auto", options: dict = {}) -> dict:
        """
        Returns:
          {
            "raw_html": str,
            "cleaned_text": str,
            "chunks": list[str],
            "mode_used": str
          }
        """
        resolved_mode = await detect_mode(url, mode)
        try:
            if resolved_mode == "playwright":
                raw_html, cleaned = await self.playwright.fetch(
                    url, wait_for_selector=options.get("wait_for_selector")
                )
            else:
                raw_html, cleaned = await self.bs4.fetch(url)
        except Exception:
            # Fallback: if Playwright fails, try BS4
            raw_html, cleaned = await self.bs4.fetch(url)
            resolved_mode = "beautifulsoup_fallback"

        from backend.engines.html_cleaner import HTMLCleaner
        chunks = HTMLCleaner().chunk(cleaned, max_chars=settings.MAX_TOKENS_PER_CHUNK * 4)

        return {
            "raw_html": raw_html,
            "cleaned_text": cleaned,
            "chunks": chunks,
            "mode_used": resolved_mode
        }

    async def save_raw_html(self, job_id: str, raw_html: str) -> str:
        path = os.path.join(settings.STORAGE_PATH, "raw", f"{job_id}.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(raw_html)
        return path
```

### 4.6 Node.js Supplementary Scraper (`node_scraper/scraper.js`)

Used as a subprocess fallback:

```javascript
const puppeteer = require('puppeteer');
const cheerio = require('cheerio');

async function scrape(url) {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64)');
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  const html = await page.content();
  await browser.close();

  const $ = cheerio.load(html);
  $('script, style, noscript').remove();
  const text = $('body').text().replace(/\s+/g, ' ').trim();

  console.log(JSON.stringify({ html, text }));
}

const url = process.argv[2];
if (!url) { console.error('URL required'); process.exit(1); }
scrape(url).catch(console.error);
```

### ✅ Phase 2 Exit Criteria
- [ ] `HTMLCleaner.clean()` strips scripts/styles from sample HTML correctly
- [ ] `BS4Engine.fetch()` returns clean text for a static site (e.g., `quotes.toscrape.com`)
- [ ] `PlaywrightEngine.fetch()` renders a JS site (e.g., `books.toscrape.com`)
- [ ] `detect_mode()` correctly identifies static vs. dynamic pages
- [ ] Node.js scraper runs: `node scraper.js https://example.com`
- [ ] `ScraperService.scrape()` returns chunks list, not empty

---

## 5. Phase 3 — Groq LLM Integration

> **Duration:** Week 2–3  
> **Goal:** Build the `GroqService` with extraction, querying, and summarization capabilities. Implement prompt templates, model selection, and chunked extraction merging.

### 5.1 Groq Service (`backend/services/groq_service.py`)

```python
from groq import Groq
from backend.config import settings
import json, re

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def extract(self, chunks: list[str], user_prompt: str) -> dict | list:
        """Extract structured data from page chunks."""
        all_results = []
        for chunk in chunks:
            messages = self._build_extraction_prompt(chunk, user_prompt)
            response = self.client.chat.completions.create(
                model=self._select_extraction_model(chunk),
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"},
                max_tokens=4096
            )
            raw = response.choices[0].message.content
            parsed = self._parse_json(raw)
            if isinstance(parsed, list):
                all_results.extend(parsed)
            elif parsed:
                all_results.append(parsed)

        # Return list if multiple records, else first item
        return all_results if len(all_results) > 1 else (all_results[0] if all_results else {})

    async def query(self, data: list | dict, user_query: str) -> dict:
        """Natural language query on stored extracted data."""
        messages = self._build_query_prompt(data, user_query)
        response = self.client.chat.completions.create(
            model=settings.GROQ_QUERY_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )
        answer = response.choices[0].message.content
        return {"answer": answer, "relevant_records": None}

    async def summarize(self, cleaned_text: str) -> str:
        """Summarize the page content."""
        messages = [
            {"role": "system", "content": "Summarize the following web page content in 3-5 sentences."},
            {"role": "user", "content": cleaned_text[:8000]}
        ]
        response = self.client.chat.completions.create(
            model=settings.GROQ_QUERY_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=512
        )
        return response.choices[0].message.content

    def _select_extraction_model(self, chunk: str) -> str:
        length = len(chunk)
        if length > 20000:
            return "mixtral-8x7b-32768"  # Large context
        elif length > 8000:
            return settings.GROQ_EXTRACTION_MODEL  # llama3-70b
        return "llama3-8b-8192"  # Fast + cheap for short pages

    def _build_extraction_prompt(self, page_text: str, user_prompt: str) -> list[dict]:
        return [
            {
                "role": "system",
                "content": (
                    "You are an expert web data extraction assistant.\n"
                    "Extract ONLY the fields specified by the user.\n"
                    "Return a JSON array if multiple records exist, or a single JSON object for one record.\n"
                    "If a field is not found, set its value to null.\n"
                    "Do NOT hallucinate. Do NOT add markdown. Return raw JSON only."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Web Page Content:\n---\n{page_text}\n---\n\n"
                    f"Extract the following: {user_prompt}\n\n"
                    "Return valid JSON only."
                )
            }
        ]

    def _build_query_prompt(self, data: any, user_query: str) -> list[dict]:
        data_str = json.dumps(data, indent=2)[:12000]  # Limit to avoid overflow
        return [
            {
                "role": "system",
                "content": (
                    "You are a data analyst. Answer the user's question based ONLY on the dataset below.\n"
                    "If the answer cannot be determined from the data, say so explicitly.\n\n"
                    f"Dataset:\n```json\n{data_str}\n```"
                )
            },
            {"role": "user", "content": user_query}
        ]

    def _parse_json(self, raw: str) -> dict | list | None:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            match = re.search(r'[\[{].*[\]}]', raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
        return None
```

### 5.2 Token Usage Tracking

Track Groq token usage per job for analytics:

```python
# Add to extract() after each API call:
token_usage = response.usage.total_tokens
# Pass back to job_service to update job.token_usage in DB
```

### 5.3 Groq Connection Verification

A simple test to verify the Groq API key works:

```python
# backend/services/groq_service.py — add method:
async def health_check(self) -> bool:
    try:
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5
        )
        return "ok" in response.choices[0].message.content.lower()
    except Exception:
        return False
```

### ✅ Phase 3 Exit Criteria
- [ ] `GroqService.extract()` returns a valid JSON dict/list for a sample cleaned text
- [ ] `GroqService.query()` answers a question about stored JSON data
- [ ] `GroqService.summarize()` returns a valid paragraph
- [ ] `_select_extraction_model()` picks the right model based on chunk length
- [ ] `health_check()` returns `True` with a valid API key
- [ ] Token usage is captured from API response

---

## 6. Phase 4 — FastAPI Backend & REST API

> **Duration:** Week 3–4  
> **Goal:** Build the complete REST API: all routers, services, background job processing, export functionality, and the `/health` endpoint.

### 6.1 App Entrypoint (`backend/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.db.database import engine, Base
from backend.routers import scrape, jobs, query, export, health

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scapper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape.router, prefix="/scrape", tags=["Scrape"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(export.router, prefix="/export", tags=["Export"])
app.include_router(health.router, prefix="/health", tags=["Health"])
```

### 6.2 Scrape Router (`backend/routers/scrape.py`)

```python
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.models.schemas import ScrapeRequest, JobResponse
from backend.services import job_service, scraper_service, groq_service

router = APIRouter()

@router.post("/", response_model=JobResponse, status_code=202)
async def submit_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job = job_service.create_job(db, request)
    background_tasks.add_task(run_scrape_pipeline, job.id, request)
    return JobResponse(job_id=job.id, status=job.status, created_at=job.created_at)

async def run_scrape_pipeline(job_id: str, request: ScrapeRequest):
    # Full pipeline: scrape → clean → Groq extract → save
    from backend.db.database import SessionLocal
    db = SessionLocal()
    try:
        job_service.update_status(db, job_id, "running")
        scrape_result = await scraper_service.ScraperService().scrape(
            str(request.url), request.mode
        )
        groq = groq_service.GroqService()
        extracted = await groq.extract(scrape_result["chunks"], request.prompt)
        raw_path = await scraper_service.ScraperService().save_raw_html(
            job_id, scrape_result["raw_html"]
        )
        job_service.save_result(db, job_id, extracted, raw_path, scrape_result["mode_used"])
        job_service.update_status(db, job_id, "completed")
    except Exception as e:
        job_service.update_status(db, job_id, "failed", str(e))
    finally:
        db.close()
```

### 6.3 Jobs Router (`backend/routers/jobs.py`)

```python
@router.get("/", response_model=list[JobDetailResponse])
def list_jobs(db: Session = Depends(get_db)):
    return job_service.get_all_jobs(db)

@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    return job_service.get_job(db, job_id)

@router.delete("/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    job_service.delete_job(db, job_id)
    return {"message": "deleted"}
```

### 6.4 Query Router (`backend/routers/query.py`)

```python
@router.post("/", response_model=QueryResponse)
async def natural_language_query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    result = job_service.get_result_data(db, request.job_id)
    groq = groq_service.GroqService()
    response = await groq.query(result, request.query)
    job_service.save_query_history(db, request.job_id, request.query, response["answer"])
    return response
```

### 6.5 Export Router (`backend/routers/export.py`)

```python
import json, csv, io
from fastapi.responses import StreamingResponse

@router.get("/{job_id}")
async def export_results(job_id: str, format: str = "json", db: Session = Depends(get_db)):
    data = job_service.get_result_data(db, job_id)
    if format == "csv":
        output = io.StringIO()
        if isinstance(data, list) and data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={job_id}.csv"}
        )
    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={job_id}.json"}
    )
```

### 6.6 Health Router (`backend/routers/health.py`)

```python
@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    groq_ok = await groq_service.GroqService().health_check()
    db_ok = True
    try:
        db.execute("SELECT 1")
    except Exception:
        db_ok = False
    return {
        "status": "ok" if groq_ok and db_ok else "degraded",
        "groq_api": "reachable" if groq_ok else "unreachable",
        "database": "connected" if db_ok else "error"
    }
```

### 6.7 Job Service (`backend/services/job_service.py`)

Full CRUD operations for jobs and results.

```python
def create_job(db, request) -> Job
def get_job(db, job_id) -> Job
def get_all_jobs(db) -> list[Job]
def update_status(db, job_id, status, error=None)
def save_result(db, job_id, data, raw_path, mode_used)
def get_result_data(db, job_id) -> dict | list
def save_query_history(db, job_id, query, answer)
def delete_job(db, job_id)
```

### 6.8 Run & Verify

```bash
cd backend
uvicorn main:app --reload --port 8000
# Open http://localhost:8000/docs for Swagger UI
```

### ✅ Phase 4 Exit Criteria
- [ ] `POST /scrape` accepts a URL and prompt, returns `job_id`
- [ ] `GET /jobs/{id}` returns status updates (queued → running → completed)
- [ ] `GET /jobs` returns list of all jobs
- [ ] `POST /query` with a `job_id` returns a Groq-generated answer
- [ ] `GET /export/{id}?format=json` downloads a valid JSON file
- [ ] `GET /export/{id}?format=csv` downloads a valid CSV file
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] Swagger UI at `/docs` shows all endpoints with correct schemas

---

## 7. Phase 5 — Next.js Frontend Dashboard

> **Duration:** Week 5–6  
> **Goal:** Build the complete Next.js dashboard with all pages and components connected to the FastAPI backend.

### 7.1 API Client (`frontend/lib/api.ts`)

Centralized API fetch wrappers:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  submitScrape: (body: ScrapeRequest) =>
    fetch(`${API_BASE}/scrape`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }).then(r => r.json()),

  getJob: (jobId: string) =>
    fetch(`${API_BASE}/jobs/${jobId}`).then(r => r.json()),

  listJobs: () =>
    fetch(`${API_BASE}/jobs`).then(r => r.json()),

  queryData: (jobId: string, query: string) =>
    fetch(`${API_BASE}/query`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ job_id: jobId, query }) }).then(r => r.json()),

  exportUrl: (jobId: string, format: 'json' | 'csv') =>
    `${API_BASE}/export/${jobId}?format=${format}`,
};
```

### 7.2 Pages to Build

| Page | Route | Components | API Calls |
|---|---|---|---|
| Dashboard Home | `/` | Stats cards, recent jobs list | `GET /jobs` |
| New Scrape | `/scrape` | `ScrapeForm` | `POST /scrape` |
| Job Queue | `/jobs` | `JobCard` list | `GET /jobs` |
| Job Detail | `/jobs/[jobId]` | Status, `ResultsTable`, export buttons | `GET /jobs/{id}` |
| NL Query | `/query` | `QueryChat` | `POST /query` |
| Export | `/export` | `ExportPanel` | `GET /export/{id}` |

### 7.3 Key Components

**`ScrapeForm.tsx`** — URL + prompt inputs with mode selector:
```
[URL Input          ] [Mode: auto ▾]
[Prompt textarea                   ]
[        Submit Scrape             ]
```

**`JobCard.tsx`** — Job status card with colored status badges:
```
🟡 Running  |  ✅ Completed  |  ❌ Failed  |  ⏳ Queued
```

**`ResultsTable.tsx`** — Dynamic column table with search:
```
[🔍 Search results... ]
| Field 1 | Field 2 | Field 3 |  ← dynamic from JSON keys
|---------|---------|---------|
| value   | value   | value   |
[Export JSON] [Export CSV]
```

**`QueryChat.tsx`** — Chat-style NL query interface:
```
┌──────────────────────────────┐
│ 💬 Which items cost < $30?  │
│                              │
│ 🤖 2 products match:        │
│    Widget Pro ($29.99)       │
│    Basic Gadget ($19.99)     │
└──────────────────────────────┘
[Ask a question...    ] [Send]
```

### 7.4 Job Polling Logic

Poll job status every 2 seconds until completed or failed:

```typescript
useEffect(() => {
  if (status === 'queued' || status === 'running') {
    const interval = setInterval(async () => {
      const job = await api.getJob(jobId);
      setJob(job);
      if (job.status === 'completed' || job.status === 'failed') {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }
}, [jobId, status]);
```

### ✅ Phase 5 Exit Criteria
- [ ] Dashboard home shows job count stats and recent jobs
- [ ] Scrape form submits successfully, redirects to job detail
- [ ] Job detail page polls and updates status in real-time
- [ ] Results table renders all extracted JSON fields as columns
- [ ] NL query chat sends question and displays Groq's answer
- [ ] JSON + CSV export buttons trigger file downloads
- [ ] All pages are responsive (mobile-friendly)

---

## 8. Phase 6 — CLI Tool

> **Duration:** Week 6  
> **Goal:** Build the Typer-based Python CLI that talks to the FastAPI backend.

### 8.1 CLI Entrypoint (`cli/main.py`)

```python
import typer
from cli.commands import scrape, jobs, query, export

app = typer.Typer(name="scapper", help="Intelligent LLM-powered web scraper")
app.add_typer(scrape.app, name="scrape")
app.add_typer(jobs.app, name="jobs")
app.add_typer(query.app, name="query")
app.add_typer(export.app, name="export")

if __name__ == "__main__":
    app()
```

### 8.2 Scrape Command (`cli/commands/scrape.py`)

```python
@app.command()
def run(
    url: str = typer.Option(..., "--url", help="URL to scrape"),
    prompt: str = typer.Option(..., "--prompt", help="Extraction prompt"),
    mode: str = typer.Option("auto", "--mode", help="Scrape mode: auto|static|dynamic"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for completion"),
):
    """Submit a scraping job."""
    ...
```

### 8.3 Jobs Command

```bash
scapper jobs list        # List all jobs with status
scapper jobs get <id>    # Get job details
scapper jobs delete <id> # Delete a job
```

### 8.4 Query Command

```bash
scapper query --job-id <id> "Which items cost less than $30?"
```

### 8.5 Export Command

```bash
scapper export --job-id <id> --format csv --output ./output.csv
scapper export --job-id <id> --format json --output ./output.json
```

### ✅ Phase 6 Exit Criteria
- [ ] `scapper --help` shows all commands
- [ ] `scapper scrape --url ... --prompt ...` triggers a job and waits for result
- [ ] `scapper jobs list` prints a formatted table of jobs
- [ ] `scapper query --job-id ... "question"` prints Groq's answer
- [ ] `scapper export --job-id ... --format csv` saves file to disk

---

## 9. Phase 7 — Error Handling, Retry & Resilience

> **Duration:** Week 7  
> **Goal:** Add comprehensive error handling, retry logic with exponential backoff, and graceful failure recovery across all layers.

### 9.1 Scraping Error Handling

| Error Scenario | Handling |
|---|---|
| Connection timeout | Retry up to `MAX_RETRIES` (default 3) with exponential backoff |
| HTTP 4xx (forbidden/bot block) | Mark job as `blocked`, store error message |
| HTTP 5xx (server error) | Retry with backoff |
| Empty page content after render | Fallback to BS4 if Playwright returned empty |
| robots.txt disallows scraping | Check before fetch; mark job as `blocked` if disallowed |

```python
# Add robots.txt check to scraper_service.py
from urllib.robotparser import RobotFileParser

async def is_allowed(url: str) -> bool:
    rp = RobotFileParser()
    robots_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt"
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch("*", url)
    except Exception:
        return True  # Allow if robots.txt is unreachable
```

### 9.2 Groq Retry Policy

Using `tenacity` for retry with exponential backoff:

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from groq import RateLimitError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(RateLimitError)
)
def _call_groq(self, **kwargs):
    return self.client.chat.completions.create(**kwargs)
```

### 9.3 JSON Validation & Retry

If Groq returns malformed JSON:

```python
# Retry with a stricter prompt
if not self._parse_json(raw):
    messages[-1]["content"] += "\n\nIMPORTANT: Return ONLY raw JSON, no markdown, no explanation."
    # Retry once more...
```

### 9.4 Global Exception Handler

```python
# backend/main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url)}
    )
```

### ✅ Phase 7 Exit Criteria
- [ ] Scraping a forbidden URL marks job as `blocked`
- [ ] Groq rate limit retries 3x with backoff (verify with mock)
- [ ] Malformed JSON from Groq triggers re-prompt
- [ ] Empty page content falls back to BS4 from Playwright
- [ ] Global exception handler returns clean JSON errors
- [ ] robots.txt check runs before every scrape

---

## 10. Phase 8 — Testing & Quality Assurance

> **Duration:** Week 8  
> **Goal:** Write unit tests, integration tests, and end-to-end smoke tests to reach ≥80% backend code coverage.

### 10.1 Backend Unit Tests

Using `pytest` + `httpx.AsyncClient`:

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

**Test files:**

```
backend/tests/
├── test_html_cleaner.py       # Test clean() and chunk()
├── test_bs4_engine.py         # Mock httpx, test fetch()
├── test_playwright_engine.py  # Mock playwright, test fetch()
├── test_groq_service.py       # Mock Groq client, test extract/query
├── test_job_service.py        # Test CRUD with in-memory SQLite
├── test_scrape_router.py      # Integration test POST /scrape
├── test_jobs_router.py        # Integration test GET /jobs
├── test_query_router.py       # Integration test POST /query
└── test_export_router.py      # Integration test GET /export
```

**Sample test:**

```python
# test_html_cleaner.py
def test_clean_removes_scripts():
    html = "<html><body><script>alert(1)</script><p>Hello</p></body></html>"
    result = HTMLCleaner().clean(html)
    assert "alert" not in result
    assert "Hello" in result

def test_chunk_splits_long_text():
    text = "word " * 5000
    chunks = HTMLCleaner().chunk(text, max_chars=100)
    assert len(chunks) > 1
    assert all(len(c) <= 110 for c in chunks)
```

### 10.2 API Integration Tests

```python
# test_scrape_router.py
async def test_submit_scrape_returns_job_id(client):
    response = await client.post("/scrape", json={
        "url": "https://quotes.toscrape.com",
        "prompt": "Extract all quotes and authors"
    })
    assert response.status_code == 202
    assert "job_id" in response.json()
```

### 10.3 Frontend Tests

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom jest
```

Test components: `ScrapeForm`, `JobCard`, `ResultsTable`, `QueryChat`.

### 10.4 End-to-End Smoke Test

Manual verification checklist:

```
1. Visit http://localhost:3000
2. Click "New Scrape" → enter URL + prompt → submit
3. Watch job status change: queued → running → completed
4. View results in ResultsTable
5. Click "Ask a question" → enter NL query → verify Groq answer
6. Click "Export JSON" → verify file downloads with correct data
7. Click "Export CSV" → verify file opens correctly in Excel/Sheets
8. Run CLI: scapper scrape --url "..." --prompt "..." → verify output
```

### 10.5 Coverage Report

```bash
pytest --cov=backend --cov-report=html tests/
# Open htmlcov/index.html → target: ≥80% coverage
```

### ✅ Phase 8 Exit Criteria
- [ ] All unit tests pass (`pytest`)
- [ ] API integration tests cover all 5 routers
- [ ] Backend test coverage ≥ 80%
- [ ] End-to-end smoke test completes without errors
- [ ] No critical security vulnerabilities (SSRF, injection)

---

## 11. Phase 9 — Dockerization & Deployment

> **Duration:** Week 9  
> **Goal:** Containerize all services with Docker Compose for local dev and document production deployment steps.

### 11.1 Backend Dockerfile (`backend/Dockerfile`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget gnupg curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Frontend Dockerfile (`frontend/Dockerfile`)

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json .

EXPOSE 3000
CMD ["npm", "start"]
```

### 11.3 Docker Compose (`docker-compose.yml`)

```yaml
version: '3.9'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: scapper
      POSTGRES_USER: scapper
      POSTGRES_PASSWORD: scapper123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      DATABASE_URL: postgresql://scapper:scapper123@db:5432/scapper
    depends_on:
      - db
    volumes:
      - ./backend/storage:/app/storage

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 11.4 Start Commands

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### ✅ Phase 9 Exit Criteria
- [ ] `docker-compose up` starts all 3 services without errors
- [ ] Backend reachable at `http://localhost:8000/docs`
- [ ] Frontend reachable at `http://localhost:3000`
- [ ] PostgreSQL data persists across container restarts
- [ ] `.env` is mounted correctly and Groq API works inside container
- [ ] Playwright runs inside Docker container

---

## 12. Phase 10 — Polish, Documentation & Final Review

> **Duration:** Week 10  
> **Goal:** Final polish, comprehensive README, project documentation, and a production-readiness review.

### 12.1 README.md

Create a professional `README.md` covering:

- Project overview + demo GIF/screenshot
- Prerequisites (Python 3.11+, Node.js 20+, Docker, Groq API key)
- Quick start (clone → `.env` setup → `docker-compose up`)
- API reference (link to `/docs`)
- CLI usage examples
- Architecture overview (link to `Docs/architecture.md`)
- Contributing guide
- License

### 12.2 `.env.example` Finalization

Ensure every required variable is documented with comments.

### 12.3 Production Readiness Checklist

```
Security:
  [ ] Groq API key not in any commit
  [ ] CORS restricted to production domain
  [ ] Input URL validated (http/https only)
  [ ] robots.txt check enforced

Performance:
  [ ] Groq call chunking prevents timeouts
  [ ] DB queries use indexed columns
  [ ] Frontend uses React.memo where appropriate

Reliability:
  [ ] All Groq calls have retry logic
  [ ] All scraper calls have timeout + fallback
  [ ] Background jobs log errors to DB

Observability:
  [ ] Structured logging with timestamps in backend
  [ ] /health endpoint monitored
  [ ] Token usage tracked per job
```

### 12.4 Final Demo Run

Full end-to-end demo across 3 different site types:

| Test Site | Type | Expected Result |
|---|---|---|
| `quotes.toscrape.com` | Static HTML | Quotes + authors extracted |
| `books.toscrape.com` | JS-rendered | Book names + prices extracted |
| A news site | Dynamic | Headlines + summaries extracted |

### ✅ Phase 10 Exit Criteria
- [ ] README covers all setup and usage steps
- [ ] Production readiness checklist items all checked
- [ ] All 3 demo test sites scrape successfully end-to-end
- [ ] NL query works on all demo results
- [ ] Docs folder contains: `problem_statement.md`, `architecture.md`, `implementation.md`

---

## 13. Dependency Graph

```
Phase 0 (Setup)
    │
    ├──► Phase 1 (DB Models)
    │         │
    │         ├──► Phase 2 (Scraping Engine)
    │         │         │
    │         │         └──► Phase 3 (Groq LLM)
    │         │                   │
    │         └─────────────────► Phase 4 (FastAPI Backend)
    │                                   │
    │                                   ├──► Phase 5 (Frontend)
    │                                   ├──► Phase 6 (CLI)
    │                                   └──► Phase 7 (Resilience)
    │
    └──────────────────────────────────► Phase 8 (Testing)
                                               │
                                               └──► Phase 9 (Docker)
                                                         │
                                                         └──► Phase 10 (Polish)
```

---

## 14. Progress Tracker

Use this table to track implementation progress:

| Phase | Status | Started | Completed | Notes |
|---|---|---|---|---|
| **Phase 0** — Environment Setup | ⬜ Not Started | — | — | |
| **Phase 1** — Database & Models | ⬜ Not Started | — | — | |
| **Phase 2** — Scraping Engine | ⬜ Not Started | — | — | |
| **Phase 3** — Groq LLM Integration | ⬜ Not Started | — | — | |
| **Phase 4** — FastAPI Backend | ⬜ Not Started | — | — | |
| **Phase 5** — Next.js Frontend | ⬜ Not Started | — | — | |
| **Phase 6** — CLI Tool | ⬜ Not Started | — | — | |
| **Phase 7** — Error Handling | ⬜ Not Started | — | — | |
| **Phase 8** — Testing & QA | ⬜ Not Started | — | — | |
| **Phase 9** — Dockerization | ⬜ Not Started | — | — | |
| **Phase 10** — Polish & Docs | ⬜ Not Started | — | — | |

**Status Legend:** ⬜ Not Started | 🔵 In Progress | ✅ Completed | ❌ Blocked

---

*This implementation plan is derived from [architecture.md](./architecture.md) and will be updated as each phase is completed.*
