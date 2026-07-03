# Design Philosophy

This project follows a "Reliability First" approach. Rather than prematurely optimizing for scale (e.g., distributed workers), the focus of Version 2 was establishing a deterministic data pipeline. By enforcing Pydantic-based schema contracts and PostgreSQL-backed state, we have created a robust foundation that makes future scaling to an asynchronous, message-queue-driven architecture both safer and more predictable.

# Architecture

## High-Level Flow

GitHub Actions
        │
        ▼
Content Ingestion
        │
        ▼
PostgreSQL
(State & Deduplication)
        │
        ▼
AI Curation
(Gemini)
        │
        ▼
Pydantic Validation
        │
        ▼
HTML Generation
        │
        ▼
Resend Email

---

## Components

### Ingestion Layer

Responsible for collecting content from configured sources.

Responsibilities

- Fetch articles
- Fetch YouTube transcripts
- Normalize data

---

### Storage Layer

Acts as the source of truth.

Responsibilities

- Persist raw content
- Prevent duplicate processing
- Maintain pipeline state

---

### AI Curation

Processes newly ingested content.

Responsibilities

- Generate summaries
- Extract technology tags
- Assign impact scores

---

### Validation Layer

Pydantic validates every LLM response before it reaches downstream systems.

Benefits

- Prevent malformed outputs
- Type safety
- Consistent downstream processing

---

### Delivery Layer

Generates responsive HTML and dispatches the briefing through Resend.

---

## Current Limitations

- Sequential ingestion
- Polling architecture
- Single worker execution
- Local logging

---

## Planned Improvements

- asyncio/httpx
- Provider abstraction
- Queue-based architecture
- Structured logging
- Retry policies
- Circuit breakers
- Semantic deduplication
