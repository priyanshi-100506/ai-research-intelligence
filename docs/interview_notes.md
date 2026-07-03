# Interview Notes

## Explain the project in one minute

I built an automated AI-powered data pipeline that collects engineering news, stores only unique articles, summarizes them using Gemini, validates every response with Pydantic, and emails a structured executive briefing every morning.

The engineering challenge wasn't summarization—it was building a reliable workflow around an LLM.

---

## Why PostgreSQL?

To maintain state.

Without persistent storage the pipeline would repeatedly summarize identical articles.

---

## Why Pydantic?

LLMs are probabilistic.

Applications require deterministic outputs.

Pydantic creates a schema contract between the model and the application.

---

## Why GitHub Actions?

Cloud scheduling.

No dependency on a local machine.

Automatic execution every day.

---

## Biggest limitation today?

Sequential processing.

As the number of sources grows, ingestion latency increases.

---

## How would you scale it?

- Async ingestion
- Worker queues
- Provider abstraction
- Retry policies
- Circuit breakers
- Better observability

---

## What did you learn?

Building AI systems is less about prompting and more about engineering reliable infrastructure around probabilistic models.
