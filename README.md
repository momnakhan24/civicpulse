# CivicPulse

**An end-to-end municipal complaint intake, triage and operations platform.**

Citizens report issues as free text. CivicPulse validates the submission, triages it with an LLM into a category, priority and one-line summary, persists it durably, and surfaces it on a live operations dashboard with aggregate statistics - with automatic fallback to deterministic rules if the AI provider is slow, rate-limited, or unavailable.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, TypeScript, nginx |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0 |
| Database | PostgreSQL 16, Alembic migrations |
| Cache | Redis 7 (stats cache + distributed rate limiter) |
| AI | Groq / Ollama, pluggable provider interface |
| Infra | Docker Compose, Kubernetes (Kustomize), GitHub Actions CI/CD |

## Architecture

Backend follows a strict four-layer separation: routes -> services -> repositories -> providers.

routes/ handles HTTP only. services/ holds business rules. repositories/ is the only layer allowed to touch SQL. providers/ wraps outbound integrations (LLM, cache) behind interfaces, so swapping a provider never touches business logic.

## Status

Work in progress. Quickstart, API reference and architecture diagram land as the backend and frontend stabilize.
