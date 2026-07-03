# Engineering Decisions

## PostgreSQL

Why?

- Persistent state
- Relational integrity
- Efficient duplicate detection

Alternative

SQLite

Reason for rejection

Not suitable for long-term hosted deployments.

---

## Pydantic

Why?

LLM outputs are probabilistic.

Pydantic converts them into deterministic validated objects.

Alternative

Manual JSON parsing

Reason for rejection

Hard to maintain and prone to runtime failures.

---

## GitHub Actions

Why?

Reliable cloud scheduling.

Alternative

Local cron jobs.

Reason for rejection

Requires a machine running continuously.

---

## SQLAlchemy

Why?

ORM abstraction while preserving relational modeling.

Alternative

Raw SQL.

Reason for rejection

Lower maintainability.

---

## HTML Emails

Why?

Better readability than plain text.

Supports structured executive briefings.
