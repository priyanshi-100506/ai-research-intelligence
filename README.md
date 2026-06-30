# Automated AI Industry Briefing Pipeline

An autonomous, production-grade data engineering pipeline that ingests raw, multi-format technical content, enforces structural data integrity, extracts high-signal industry insights using a validated LLM orchestration layer, and delivers a structured executive briefing directly to an email inbox every day.

---

# Architecture Overview

The system operates as a fully decoupled, cloud-native architecture that processes data through four distinct lifecycle stages:

### 1. Ingestion Layer

Custom asynchronous Python scrapers collect content from targeted AI and engineering publications while automatically extracting transcripts from selected technical YouTube channels using:

* `youtube-transcript-api`
* `yt-dlp`

The ingestion layer continuously gathers raw, unstructured technical content from multiple sources.

---

### 2. Storage & Deduplication

Incoming payloads are stored inside a managed PostgreSQL database hosted on Render.

Using SQLAlchemy, the pipeline enforces relational constraints and performs strict deduplication before any AI processing occurs. This guarantees that only newly discovered content is analyzed, reducing inference costs while maintaining database integrity.

---

### 3. Structured Intelligence Layer

To minimize the probabilistic nature of LLM-generated outputs, the curation engine combines **Gemini 2.5 Flash** with strict **Pydantic v2** schema validation.

Every model response is validated against predefined schemas, producing deterministic structured JSON containing:

* Executive summaries
* Technology tags
* Category classification
* Impact metrics
* Source metadata

This validation layer ensures downstream automation always receives predictable, machine-readable outputs.

---

### 4. Automation & Delivery

The complete workflow is orchestrated through GitHub Actions running on a scheduled cron workflow.

Every morning at **01:30 UTC (07:00 IST)**, the automation pipeline:

1. Executes the ingestion pipeline
2. Processes and validates new content
3. Generates an HTML executive briefing
4. Sends the newsletter through the Resend transactional email API

The system operates without manual intervention.

---

# Technical Stack

| Component             | Technology              |
| --------------------- | ----------------------- |
| Language              | Python 3.13             |
| Dependency Management | `uv`                    |
| Database              | PostgreSQL (Render)     |
| ORM                   | SQLAlchemy              |
| AI Model              | Gemini 2.5 Flash        |
| Validation            | Pydantic v2             |
| API Framework         | FastAPI                 |
| ASGI Server           | Uvicorn                 |
| Automation            | GitHub Actions          |
| Email Delivery        | Resend                  |
| Containerization      | Docker & Docker Compose |

---

# Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── daily_briefing.yml
│
├── app/
│   ├── agents/
│   ├── database/
│   ├── scrapers/
│   └── services/
│
├── docker/
├── frontend/
│
├── .env
├── docker-compose.yml
├── main.py
├── pyproject.toml
├── requirements.txt
├── run_pipeline.py
├── test_ai.py
├── test_scrapers.py
└── uv.lock
```

### Directory Overview

| Directory/File    | Purpose                                                            |
| ----------------- | ------------------------------------------------------------------ |
| `app/agents`      | LLM orchestration, prompt engineering, and structured AI workflows |
| `app/database`    | SQLAlchemy models, database engine, and persistence layer          |
| `app/scrapers`    | RSS, website, YouTube, and transcript ingestion modules            |
| `app/services`    | Business logic, briefing generation, and email delivery            |
| `frontend/`       | Future dashboard and visualization layer                           |
| `docker/`         | Container runtime configuration                                    |
| `run_pipeline.py` | Main pipeline execution entry point                                |
| `main.py`         | FastAPI application entry point                                    |

---

# Environment Variables

Configure the following environment variables locally or as GitHub Repository Secrets.

| Variable         | Description                  | Example                              |
| ---------------- | ---------------------------- | ------------------------------------ |
| `DATABASE_URL`   | PostgreSQL connection string | `postgresql://user:password@host/db` |
| `GEMINI_API_KEY` | Google AI Studio API key     | `AIzaSy...`                          |
| `RESEND_API_KEY` | Resend API key               | `re_...`                             |

---

# Local Installation

This project uses **uv** for fast dependency and environment management.

## 1. Clone the Repository

```bash
git clone https://github.com/priyanshi-100506/ai-news-aggregator.git
cd ai-news-aggregator
```

---

## 2. Create a Virtual Environment

```bash
uv venv
```

Activate it:

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

---

## 4. Run the Pipeline

```bash
uv run python run_pipeline.py
```

---

# Production Deployment

## PostgreSQL Database

Provision a managed PostgreSQL instance on Render and configure the **External Database URL** as the value of `DATABASE_URL`.

This allows both local development and GitHub-hosted runners to connect securely.

---

## GitHub Actions Automation

The pipeline is scheduled using:

```
.github/workflows/daily_briefing.yml
```

```yaml
on:
  schedule:
    - cron: '30 1 * * *'
  workflow_dispatch:
```

This schedule executes the workflow automatically every day at:

* **01:30 UTC**
* **07:00 AM IST**

The `workflow_dispatch` trigger also enables manual execution directly from the GitHub Actions interface.

---

# Workflow Summary

```text
Technical Sources
        │
        ▼
 Async Python Scrapers
        │
        ▼
 PostgreSQL Database
        │
        ▼
 Deduplication Layer
        │
        ▼
 Gemini 2.5 Flash
        │
        ▼
 Pydantic Validation
        │
        ▼
 HTML Brief Generator
        │
        ▼
 GitHub Actions
        │
        ▼
 Resend API
        │
        ▼
 Daily Executive Briefing
```

---

# Key Features

* Automated multi-source AI news aggregation
* Asynchronous scraping architecture
* YouTube transcript ingestion
* PostgreSQL-backed persistent storage
* SQLAlchemy ORM with deduplication
* Structured LLM outputs using Pydantic schemas
* Daily executive briefing generation
* Automated GitHub Actions scheduling
* Responsive HTML email delivery via Resend
* Docker-ready deployment architecture

---

# Future Enhancements

* Interactive web dashboard
* Searchable article archive
* Topic-based filtering
* Semantic vector search
* User subscription management
* Analytics and engagement tracking
* REST API endpoints for external integrations

---

# License

This project is intended for educational and portfolio purposes. Feel free to fork, modify, and extend the pipeline for your own use.
