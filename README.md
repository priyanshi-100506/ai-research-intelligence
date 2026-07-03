# AI Industry Briefing Pipeline

An automated AI-powered data engineering pipeline that collects engineering news, validates LLM-generated insights, and delivers a structured executive briefing directly to email.

---

## Why I Built This

Keeping up with engineering blogs, AI announcements, and technical videos every day became increasingly difficult.

Instead of manually filtering dozens of sources, I built an automated pipeline that continuously ingests content, stores only new information, summarizes it using an LLM, validates every response through strict schemas, and generates a daily HTML briefing.

The goal of this project was not simply to use an LLM—it was to engineer a reliable service around one.

---

## Architecture

GitHub Actions (Scheduler)

↓

Ingestion Layer

↓

PostgreSQL Storage & Deduplication

↓

Gemini AI Curation

↓

Pydantic Schema Validation

↓

HTML Report Generation

↓

Email Delivery (Resend)

---

## Features

- Automated scheduled execution using GitHub Actions
- PostgreSQL-backed state management
- Duplicate detection before AI processing
- Structured LLM outputs with Pydantic
- Responsive HTML email generation
- Production-oriented project structure
- Unit testing with pytest

---

## Tech Stack

- Python
- PostgreSQL
- SQLAlchemy
- Pydantic v2
- Gemini 2.5 Flash
- GitHub Actions
- Resend
- pytest

---

## Documentation

Additional engineering documentation is available inside the **docs/** folder.

- Architecture
- Engineering Decisions
- Interview Notes
- Future Improvements

---

Built by Priyanshi Chirag Shah
