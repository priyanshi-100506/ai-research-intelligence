# AI Research Intelligence Platform

An AI-powered research intelligence platform that automatically ingests recent AI research papers, generates structured insights using Google Gemini, validates every AI response using strict schemas, and serves curated research through a FastAPI dashboard and REST API.

Built with asynchronous backend architecture, PostgreSQL persistence, Docker, and a production-oriented project structure.

---

# Why I Built This

Hundreds of AI research papers are published every day across domains like Large Language Models, Computer Vision, Robotics, and AI Agents. Manually tracking these papers is time-consuming and inefficient.

This project automates the complete research curation workflow by:

- Collecting newly published research papers from arXiv
- Persisting only unseen papers into PostgreSQL
- Generating structured summaries using Gemini 2.5 Flash
- Validating every AI response with Pydantic schemas
- Serving curated research through a FastAPI dashboard and REST API

The objective was not simply to use an LLM, but to engineer a reliable backend system around one.

---

# System Architecture

```text
                        AI Research Intelligence Platform

                                Research Sources
                                      │
                                      ▼
                             arXiv Research API
                                      │
                                      ▼
                         Research Ingestion Pipeline
                                      │
                                      ▼
                 PostgreSQL (Neon) + Duplicate Detection
                                      │
                         Only New Research Papers
                                      ▼
                      Gemini 2.5 Flash AI Processing
                                      │
                                      ▼
                     Pydantic v2 Schema Validation
                                      │
                                      ▼
                 SQLAlchemy Async ORM + AsyncPG Storage
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
      FastAPI REST API                             Jinja2 Dashboard
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      ▼
                               Docker Containers
                                      │
                                      ▼
                         CI/CD Ready Deployment Pipeline
```

---

# Features

- Automated AI research paper ingestion from arXiv
- Asynchronous FastAPI backend
- PostgreSQL (Neon) persistent storage
- Duplicate detection before AI processing
- AI-powered research summarization using Google Gemini 2.5 Flash
- Structured output validation using Pydantic v2
- Async SQLAlchemy + AsyncPG database operations
- Category-based research organization
- REST API with automatic OpenAPI/Swagger documentation
- Server-side rendered dashboard using Jinja2 templates
- Responsive UI styled with Tailwind CSS
- Dockerized development environment
- Production-oriented modular architecture
- CI/CD-ready project structure

---

# Tech Stack

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.0
- AsyncPG
- PostgreSQL (Neon)
- Google Gemini 2.5 Flash
- Pydantic v2

### Frontend

- Jinja2 Templates
- HTML5
- Tailwind CSS

### DevOps

- Docker
- Docker Compose
- uv
- Git
- GitHub

---

# Project Structure

```
AI-Research-Intelligence-Platform/
│
├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── database/
│   ├── templates/
│   ├── static/
│   └── main.py
│
├── docs/
├── docker/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

# Current Workflow

1. Fetch latest research papers from arXiv
2. Check PostgreSQL for duplicate papers
3. Store only unseen research
4. Send research abstract to Gemini
5. Generate structured summary, category and insights
6. Validate response using Pydantic schemas
7. Persist curated research
8. Display results through REST API and dashboard

---

# Documentation

The **docs/** directory contains engineering documentation including:

- System Architecture
- Engineering Decisions
- Database Design
- Future Roadmap
- Interview Notes

---

# Roadmap

- React + Vite frontend
- Real-time dashboard updates
- Advanced search & filtering
- Automated scheduling
- Email digest generation
- Structured logging
- Monitoring & observability
- Authentication
- Personalized research feeds
- GitHub Actions CI/CD deployment

---

# Engineering Highlights

- Asynchronous backend architecture
- Production-inspired layered design
- Strict schema validation for deterministic LLM outputs
- Separation of concerns using service architecture
- Dockerized for reproducible environments
- Cloud PostgreSQL integration
- CI/CD-ready deployment architecture

---

## Built By

**Priyanshi Shah**
