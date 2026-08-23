# LEARNINGS.md — What It Took to Build Metis

> A honest account of every decision, tradeoff, bug, and lesson learned while building this project. Read this to understand *why* things are the way they are.

---

## What Metis Actually Does

At its core, Metis is a **scheduled data pipeline with a real-time frontend**:

```
ArXiv API → Scraper → Dedup → Gemini Curation → PostgreSQL → SSE → React UI
```

Every 6 hours, APScheduler wakes up, fetches the latest AI papers from ArXiv, runs each one through Gemini 2.5 Flash for structured curation, saves it to Neon Postgres, and broadcasts each result live to any connected dashboard via Server-Sent Events.

Simple idea. Surprisingly many decisions to get right.

---

## Key Engineering Decisions

### 1. Why FastAPI over Flask/Django?

**Decision:** FastAPI  
**Why:** The pipeline is inherently async — scraping, DB writes, Gemini API calls, SSE streaming. Flask is sync-first (WSGI), Django is heavy. FastAPI is async-native (ASGI), built on Pydantic v2, and auto-generates OpenAPI docs. No contest.

**Tradeoff:** FastAPI has a steeper learning curve if you're new to async Python, dependency injection patterns, and Pydantic models.

---

### 2. Why Pydantic v2 for LLM output validation?

**Decision:** Pydantic `BaseModel` + `response_schema` in the Gemini API call  
**Why:** LLMs are non-deterministic. Asking Gemini to return JSON and hoping for the best is a recipe for `KeyError` in production. By passing `response_schema=ArticleSummary`, the Gemini API is forced to return structured output matching the schema — and Pydantic validates it on the way in.

```python
class ArticleSummary(BaseModel):
    summary: str
    impact_score: float
    tech_stack: str
    justification: str
    category: str  # must be 'NLP', 'Vision', or 'Robotics'
```

**Tradeoff:** Category is constrained to 3 values. Papers that don't fit cleanly (e.g. a multimodal paper) get assigned the closest category by the model. A richer taxonomy would need more prompt engineering.

---

### 3. Why Server-Sent Events (SSE) over WebSockets?

**Decision:** SSE (`/stream` endpoint)  
**Why:** The communication is **one-directional** — server pushes, client only reads. WebSockets are overkill for this use case and harder to manage (connection state, reconnect logic, load balancers). SSE is just HTTP, works through proxies/CDNs, and natively reconnects.

**The broadcaster pattern:**
```python
class NewsBroadcaster:
    subscribers: Set[asyncio.Queue]
    
    async def broadcast(self, data):
        for queue in self.subscribers:
            await queue.put(data)  # non-blocking push to all listeners
```

Each connected client gets its own `asyncio.Queue`. When a paper is curated, `broadcaster.broadcast()` fans it out to all queues simultaneously.

**Tradeoff:** SSE doesn't work well if you need bidirectional communication. Also, Render's free tier spins down after 15 min — clients get disconnected and need to reconnect. The frontend handles this with a reconnect loop.

---

### 4. Why Neon (serverless Postgres) over SQLite?

**Decision:** Neon Postgres with AsyncPG  
**Why:** SQLite is local-file-based — it doesn't work across multiple Render instances and has no native async driver. Neon gives us a real Postgres database with a free tier, async-compatible via AsyncPG, and SSL-required connections for security. Deduplication at the DB level (via `UNIQUE` constraint on `article_id`) is atomic and race-condition safe.

**Tradeoff:** Cold start latency. Neon serverless branches spin down — the first query after inactivity takes slightly longer. The `pool_pre_ping=True` setting in the engine detects stale connections automatically.

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,    # health-check connections before use
    pool_recycle=3600,     # recycle hourly to prevent stale connections
)
```

---

### 5. Why APScheduler over Celery/cron?

**Decision:** `APScheduler` with `AsyncIOScheduler`  
**Why:** Celery requires a message broker (Redis/RabbitMQ) — heavy infrastructure for a side project. Cron is external and stateless. APScheduler runs **inside** the FastAPI process, shares the same event loop, and needs zero additional services.

```python
scheduler.add_job(
    scheduled_ingestion_task,
    trigger=IntervalTrigger(hours=6),
    max_instances=1,  # prevents overlapping runs
)
```

**Tradeoff:** If the server crashes or restarts, the schedule resets. For a production system processing financial data you'd want an external scheduler. For a research aggregator running every 6 hours, it's fine.

**Bug we hit:** Originally used `datetime.now()` (naive/timezone-unaware) as `next_run_time`. APScheduler uses UTC internally — this caused a `TypeError`. Fixed to `datetime.now(timezone.utc) + timedelta(seconds=30)` to also give DB tables time to initialize before first run.

---

### 6. Why uv over pip/poetry?

**Decision:** `uv` for dependency management  
**Why:** `uv` is 10–100x faster than pip for dependency resolution and installation. It also manages virtual environments, handles lockfiles (`uv.lock`), and the `uv run` command ensures commands execute in the correct environment without activating it manually.

**Render deployment command:**
```yaml
buildCommand: pip install uv && uv sync
startCommand: uv run uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Bug we hit:** First deployment used `uv pip install --system` which installed packages but didn't put binaries on `$PATH`. `uvicorn: command not found`. Fixed by switching to `uv run uvicorn` which resolves the venv automatically.

---

### 7. Why two config files? (`config.py` and `core/config.py`)

**Honest answer:** This was a refactoring artifact.

The project started with `core/config.py` (a tighter module). During a refactor to add `PIPELINE_SECRET` and `ALLOWED_ORIGINS`, a second `src/ai_news_aggregator/config.py` was created with those new fields, while `core/config.py` was left behind with stricter required fields.

**The bug this caused on Render:** `core/config.py` had `RESEND_API_KEY`, `NEWS_API_KEY`, and `RECIPIENT_EMAIL` as **required fields** (no defaults). They weren't set in Render → Pydantic validation error → crash on startup.

**Fix:** Made them optional with `= ""` defaults in `core/config.py`.

**Better long-term fix:** Consolidate into a single `config.py`. The duplication is technical debt.

---

### 8. Import path inconsistency (`src.ai_news_aggregator` vs `ai_news_aggregator`)

**The problem:** Some files import as:
```python
from src.ai_news_aggregator.services.pipeline_service import PipelineService
```
Others import as:
```python
from ai_news_aggregator.database.models import SessionLocal
```

**Why it happened:** The project was initially run directly from the root (where `src/` is visible). When installed as a package (`uv sync`), the package is importable as `ai_news_aggregator`. But `main.py` still uses `src.` prefix because it runs from the project root.

**Why it works in production:** `uv run` sets `PYTHONPATH` to include the project root, so `src.ai_news_aggregator` resolves fine.

**Better long-term fix:** Standardize all imports to `ai_news_aggregator.*` (no `src.` prefix).

---

## Bugs Fixed During This Build

| Bug | Root Cause | Fix |
|---|---|---|
| `uvicorn: command not found` on Render | `uv pip install --system` doesn't put binaries on `$PATH` | Switched to `uv run uvicorn` |
| `RESEND_API_KEY Field required` crash | `core/config.py` had optional vars as required | Added `= ""` defaults |
| `published_date` AttributeError in API | `api.py` used `s.published_date` but model column is `published_at` | Fixed field name reference |
| Archive tests causing import errors | pytest collected `archive/` directory | Added `norecursedirs = ["archive"]` in `pyproject.toml` |
| `test_ai.py` importing `app.services.curator_service` | Old module path from pre-refactor era | Updated to `src.ai_news_aggregator.services.curation_service` |
| `test_ingestion.py` calling `run_ingestion()` | Method was renamed to `run_pipeline()` | Fixed method call |
| Async test functions failing | Missing `@pytest.mark.asyncio` decorators | Added decorators + `pytest-asyncio` |
| `datetime.now()` deprecation in scheduler | Naive datetime passed to timezone-aware APScheduler | Fixed to `datetime.now(timezone.utc)` |
| `test_pipeline.py` taking 2+ minutes | Test ran full ArXiv scrape + 20 Gemini calls | Added `monkeypatch` to mock `fetch_papers` |

---

## What the Architecture Gets Right

- **Deduplication is O(1) per paper** — bulk-fetch all existing IDs in one query, filter in Python. No N+1 queries.
- **Curation failures are graceful** — if Gemini fails for one paper, a dummy fallback is used and processing continues.
- **SSE keep-alive** — every 15 seconds, a `: keep-alive` comment is sent to prevent proxies from closing idle connections.
- **Rate limiting at the router level** — SlowAPI limits `/trigger-pipeline` to 5 req/min per IP.
- **Secret-optional dev mode** — if `PIPELINE_SECRET` is not set, the endpoint is open. Local dev works without any config.

---

## What Could Be Better

| Area | Current State | Ideal State |
|---|---|---|
| Import paths | Mixed `src.` / non-`src.` prefix | All use `ai_news_aggregator.*` |
| Config duplication | Two `Settings` classes | Single `config.py` |
| Category taxonomy | 3 categories (NLP/Vision/Robotics) | 6+ including Multimodal, RL, etc. |
| Scheduler reliability | In-process APScheduler | External cron or Render cron job |
| Test coverage | 3 integration tests | Unit tests per service + mocked DB |
| Email digest | Implemented but not connected | Wired to scheduler |
| Blog scraper | Code exists, not in pipeline | Integrated alongside ArXiv |
| Pagination | Not implemented | Cursor-based pagination on `/articles` |
| Sync sessions in email/blog | Old `SessionLocal` (sync) left over | Migrate to `AsyncSessionLocal` |

---

## Lessons Learned

1. **Always validate LLM output with a schema.** Trusting string JSON from an LLM is fragile. Pydantic + structured response formats is the correct pattern.

2. **Make optional env vars optional in code too.** If a feature is optional (email digest), its env vars should have defaults. Don't make the whole app undeployable because someone didn't set `RESEND_API_KEY`.

3. **Test your deployment commands before pushing.** `uvicorn: command not found` would have been caught by running `uv run uvicorn` once in a fresh shell.

4. **Async requires async all the way down.** Mixing sync and async SQLAlchemy in the same codebase is confusing and bug-prone. Pick one and migrate fully.

5. **The `src/` layout adds import complexity.** When running directly vs installed as a package, import resolution differs. Standardize early.

6. **SSE is underrated for real-time UIs.** WebSockets get all the press, but for unidirectional push (server → client), SSE is simpler, more resilient, and HTTP-native.

7. **monkeypatch in tests is essential for LLM-dependent code.** Without mocking the scraper and Gemini calls, tests take minutes and cost API credits. Always mock external calls in unit/integration tests.

---

Built by [Priyanshi Shah](https://github.com/priyanshi-100506)  
Repo: [github.com/priyanshi-100506/metis](https://github.com/priyanshi-100506/metis)
