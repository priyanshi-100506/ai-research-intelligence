# Metis — AI Research Intelligence

> An automated, full-stack research platform that ingests AI papers from ArXiv, scores and summarises them with **Gemini 2.5 Flash**, and streams curations in real time to a React dashboard — engineered for reliability, not just vibes.

---

## Why I Built This

The volume of AI research published daily makes it genuinely hard to stay current across NLP, Vision, Robotics, and related fields. Instead of a scraper bolted to a ChatGPT prompt, I wanted to build something *properly engineered*:

- **Reliability** — deduplication, Pydantic schema validation, graceful fallbacks
- **Real-time feedback** — Server-Sent Events stream new curations to the UI as they happen
- **Correct LLM integration** — structured output enforced at the schema level, not by hoping the model behaves
- **Production architecture** — async throughout, modular routers, env-driven config, rate limiting

---

## Architecture

```
ArXiv API
    │
    ▼
ArXiv Scraper          ← fetches candidate papers
    │
    ▼
Deduplication          ← bulk ID check, skips already-stored entries
    │
    ▼
Gemini Curation        ← summary · impact score · category · tech stack
Pydantic v2 validation ← enforces structure on every LLM response
    │
    ├──► PostgreSQL (Neon)   ← persistent storage
    │
    └──► SSE Broadcaster     ← live stream to dashboard
              │
              ▼
         React Dashboard (Metis)
         REST API  /api/v1/articles
```

**Scheduling:** APScheduler triggers the pipeline every 6 hours automatically.  
**On-demand:** `POST /api/v1/trigger-pipeline` (rate-limited, token-protected).

---

## Features

- **Automated ingestion** — ArXiv papers fetched and stored on a 6-hour schedule
- **Intelligent deduplication** — bulk ID check before any Gemini call is made
- **Gemini 2.5 Flash curation** — summary, impact score (0–10), category, tech stack, justification
- **Pydantic v2 validation** — every LLM response is structurally verified
- **Server-Sent Events** — new curations stream to the dashboard in real time
- **React + Vite dashboard** — warm beige/terracotta palette, filtering, live toast notifications
- **Secured pipeline trigger** — 5 req/min rate limit + optional `X-Pipeline-Secret` token auth
- **Neon serverless Postgres** — async SQLAlchemy + AsyncPG
- **Deploy-ready** — `vercel.json` (frontend) + `render.yaml` (backend) included

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI · Uvicorn · Python 3.11+ |
| Database | PostgreSQL (Neon serverless) |
| ORM / Driver | SQLAlchemy 2.0 async · AsyncPG |
| Schema validation | Pydantic v2 |
| AI model | Google Gemini 2.5 Flash |
| Scheduling | APScheduler |
| Rate limiting | SlowAPI |
| Dependency manager | uv |
| Frontend | React 19 · Vite 6 · Tailwind CSS 3 |
| Icons | Lucide React |
| Frontend deploy | Vercel |
| Backend deploy | Render |

---

## Local Development

### Prerequisites
- Python 3.11+ · Node.js 18+ · [uv](https://docs.astral.sh/uv/)

### 1. Clone & configure

```bash
git clone https://github.com/priyanshi-100506/metis.git
cd metis
```

Create `.env` in the project root:

```env
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>/<db>
GEMINI_API_KEY=your_gemini_api_key

# Optional — leave blank for open dev access:
PIPELINE_SECRET=
ALLOWED_ORIGINS=
```

### 2. Start the backend

```bash
uv run uvicorn main:app --reload
# API → http://localhost:8000
# Docs → http://localhost:8000/docs
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard → http://localhost:5173
```

### 4. Trigger the pipeline

```powershell
Invoke-WebRequest -Method Post -Uri "http://127.0.0.1:8000/api/v1/trigger-pipeline"
```

---

## Environment Variables

### Backend (`.env`)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | `postgresql+asyncpg://...` connection string |
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |
| `PIPELINE_SECRET` | ⬜ | Token for `/trigger-pipeline`. Omit for open dev access |
| `ALLOWED_ORIGINS` | ⬜ | Comma-separated production frontend URLs for CORS |

### Frontend (`frontend/.env.local` or Vercel dashboard)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | ✅ | e.g. `https://your-api.onrender.com/api/v1` |
| `VITE_STREAM_URL` | ✅ | e.g. `https://your-api.onrender.com/stream` |
| `VITE_PIPELINE_SECRET` | ⬜ | Must match `PIPELINE_SECRET` on backend |

---

## Deployment

### Backend → Render

1. Push repo to GitHub
2. **Render** → New Web Service → connect repo → Render auto-detects `render.yaml`
3. Set env vars in Render dashboard (`DATABASE_URL`, `GEMINI_API_KEY`, `PIPELINE_SECRET`)
4. Note your service URL: `https://metis-api.onrender.com`

### Frontend → Vercel

1. **Vercel** → New Project → import repo → set **Root Directory** to `frontend`
2. Add env vars: `VITE_API_BASE_URL`, `VITE_STREAM_URL`, `VITE_PIPELINE_SECRET`
3. Deploy → note your URL: `https://metis-xyz.vercel.app`

### Wire CORS (critical)

Back in Render → Environment → set:
```
ALLOWED_ORIGINS=https://metis-xyz.vercel.app
```
Then **Manual Deploy → Deploy latest commit**.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/articles` | List curated articles — filterable by `min_score` & `category` |
| `POST` | `/api/v1/trigger-pipeline` | Trigger ingestion pipeline (202 Accepted) · 5 req/min · token auth |
| `GET` | `/stream` | SSE stream of live curations |
| `GET` | `/docs` | Swagger UI |

---

## Project Structure

```
ai-news-aggregator/
├── main.py                              # App factory, CORS, rate limiter
├── pyproject.toml                       # Python deps (uv)
├── render.yaml                          # Render deployment blueprint
├── Dockerfile / docker-compose.yml
│
├── src/ai_news_aggregator/
│   ├── config.py                        # Pydantic settings
│   ├── database/models.py               # SQLAlchemy ORM
│   ├── scrapers/arxiv_scraper.py
│   ├── services/
│   │   ├── pipeline_service.py          # Orchestrates scrape → curate → save → broadcast
│   │   ├── curation_service.py          # Gemini + Pydantic validation
│   │   └── scheduler.py                 # APScheduler 6-hour job
│   ├── routers/
│   │   ├── api.py                       # REST endpoints
│   │   └── stream.py                    # SSE endpoint
│   └── core/shared.py                   # SSE broadcaster singleton
│
└── frontend/
    ├── vercel.json
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── App.jsx
        ├── components/ResearchCard.jsx
        ├── components/Toast.jsx
        └── hooks/useSSE.js
```

---

## Roadmap

- [x] ArXiv ingestion pipeline with deduplication
- [x] Gemini AI curation · Pydantic v2 validation
- [x] APScheduler automated runs
- [x] Real-time SSE dashboard
- [x] React + Vite frontend (Metis)
- [x] Rate-limited · token-protected pipeline trigger
- [x] Vercel + Render deployment configs
- [ ] Pagination / infinite scroll
- [ ] Full-text search
- [ ] Email digest (Resend)
- [ ] Saved / bookmarked papers
- [ ] Personalised feeds per topic

---

Built by [**Priyanshi Shah**](https://github.com/priyanshi-100506)
