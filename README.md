# AI Industry Briefing Pipeline

An autonomous, production-grade data engineering pipeline that ingests technical content, enforces structural data integrity, and delivers validated executive briefings directly to the inbox.

## Architectural Philosophy
This project was built to move beyond simple automation. It treats AI models, third-party news providers, and email services as **volatile dependencies**. By wrapping these components in defensive logic, structural validation, and robust observability, the system achieves a level of reliability that transcends basic script-based automation.

## Engineering Principles
- **Observability:** Centralized logging replaces ephemeral console output. Every execution event is captured with timestamps and severity levels, allowing for post-mortem diagnostics via logs/pipeline.log.
- **Reliability:** The system employs defensive API handling. Instead of generic crash-on-error patterns, the pipeline distinguishes between transient network failures, rate-limiting (429), and authentication errors (403), allowing for graceful degradation.
- **Extensibility:** Designed with modularity in mind. The ingestion layer is decoupled from the storage and curation layers, facilitating future integration of additional data providers.
- **CI/CD:** Automated execution via GitHub Actions with integrated validation tests, ensuring environment integrity before any dispatch.

## Core Stack
- **Language:** Python 3.13
- **Orchestration:** GitHub Actions (Cron-scheduled)
- **Validation:** Pydantic v2
- **Data Integrity:** SQLAlchemy / PostgreSQL
- **AI Integration:** Gemini 2.5 Flash
- **Data Source:** Currents News API
- **Transactional Email:** Resend API

## System Design
1. **Data Source Strategy:** 
   - **Currents API:** Serves as the primary news acquisition layer. 
   - **Defensive Integration:** The pipeline actively monitors HTTP response codes (specifically 429 Rate Limits and 403 Access errors) and API headers to manage consumption and ensure system stability.
2. **Buffering:** Raw payloads are committed to PostgreSQL prior to AI analysis, ensuring that no data is lost if the downstream curation layer encounters issues.
3. **Curation:** AI inference is strictly constrained by Pydantic schemas, ensuring deterministic, machine-readable output.
4. **Delivery:** Automated HTML report generation via transactional email services.

## Pipeline Lifecycle
- **Health Checks:** CI/CD triggers pytest to validate connectivity and configuration before runtime.
- **Data Acquisition:** Defensive scraping with retry-aware logic and structured logging.
- **State Management:** Logs are persisted for auditing, and errors are categorized by severity levels (INFO/WARNING/ERROR) to facilitate quick debugging.

---
*Built by Priyanshi Chirag Shah | Engineering Laboratory Initiative*
