# Metis — AI Research Intelligence Platform

An AI-powered research intelligence platform that automatically ingests recent AI research papers, generates structured insights using an LLM, validates every response with strict schemas, and serves curated research through a FastAPI dashboard and REST API.

---

# Why I Built This

The volume of AI research published every day makes it difficult to stay updated with the latest developments across Natural Language Processing, Computer Vision, Robotics, and other domains.

Instead of manually browsing research repositories, I built an automated backend pipeline that continuously ingests research papers, stores only new entries, generates structured AI summaries, validates every response using strict schemas, and exposes the curated results through a web dashboard and API.

The objective of this project was not simply to integrate an LLM, but to engineer a reliable backend system around one.

---

## Architecture

FastAPI Backend

↓

Research Ingestion (arXiv)

↓

PostgreSQL Storage & Deduplication

↓

Gemini AI Curation

↓

Pydantic Schema Validation

↓

REST API & Dashboard

---

## Features

* Automated research paper ingestion from arXiv
* PostgreSQL-backed persistent storage
* Duplicate detection before AI processing
* AI-powered research summarization using Gemini 2.5 Flash
* Structured LLM output validation using Pydantic v2
* Asynchronous database operations with SQLAlchemy and AsyncPG
* Category-based research organization
* FastAPI REST API with interactive documentation
* Dockerized development environment
* Modular, production-inspired project architecture

---

# Tech Stack

* Python 3.13
* FastAPI
* PostgreSQL (Neon)
* SQLAlchemy 2.0
* AsyncPG
* Pydantic v2
* Google Gemini 2.5 Flash
* Docker & Docker Compose
* Jinja2
* Tailwind CSS
* uv

---

## Documentation

Additional engineering documentation is available inside the **docs/** folder.

* System Architecture
* Engineering Decisions
* Future Roadmap
* Project Design Notes

---

# Roadmap

* React + Vite frontend
* Advanced search and filtering
* Improved deduplication pipeline
* Structured logging and monitoring
* Automated scheduling
* Real-time dashboard updates
* User authentication
* Personalized research feeds

---

Built by **Priyanshi Shah**
