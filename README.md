# Embeddable RAG Ask-Widget

A self-hosted, embeddable AI support widget that businesses can drop into their website with a single script tag. It answers customer questions using Retrieval-Augmented Generation (RAG) grounded in the business's own documents — with guardrails, caching, and observability built in as first-class concerns, not afterthoughts.

Unlike SaaS chat-widget products, this is designed to be **self-hosted**: a business clones/deploys this backend themselves, uploads their own documents, and owns their own data end-to-end.

## Why this exists

Most "AI chatbot for your website" tools are black boxes — you don't know what they retrieve, whether they hallucinate, or where your data goes. This project takes the opposite approach: every stage of the pipeline (retrieval, generation, caching, safety checks) is explicit, inspectable, and traced.

## Architecture

    Client's Website
          │
          <script src="widget.js"> │ ▼ FastAPI Backend (this repo) │ ┌──────────┼──────────────────────────────┐ ▼ ▼ ▼ Postgres Qdrant Redis (metadata, (vector search: (exact-match + documents) documents + semantic cache) rate limiting) │ ▼ ┌─────────────────────────────┐ │ Agentic-style Chat Flow │ │ 1. Prompt injection screen │ │ 2. PII redaction │ │ 3. Semantic cache lookup │ │ 4. Embed question │ │ 5. Retrieve relevant chunks │ │ 6. No-hallucination floor │ │ (refuse if no context) │ │ 7. Generate (Ollama, local) │ │ 8. Cache + trace result │ └─────────────────────────────┘ │ ▼ LangSmith (full tracing: retrieval, generation, cache) ```` ## Features **Document ingestion** - Upload PDF/TXT documents via a REST API - Text extraction (`pypdf`) and recursive, separator-aware chunking (paragraph → sentence → word → character fallback) - Background processing (upload returns immediately; embedding happens asynchronously) - File type and size validation **Retrieval-Augmented Generation** - Local, free embeddings (`sentence-transformers`, `BAAI/bge-small-en-v1.5`) - Vector storage and similarity search via Qdrant, with a minimum relevance score threshold - Local, free LLM generation via Ollama — no API costs, no data leaving the host machine - A hard **no-hallucination floor**: if no sufficiently relevant context is retrieved, the system refuses to answer rather than guessing **Guardrails** - Prompt injection screening on all user input (regex-based, layered defense) - PII detection and redaction (emails, phone numbers, card-like patterns) before anything reaches the LLM or logs - Input validated end-to-end with Pydantic v2 **Performance** - Two-tier caching: exact-match (Redis) and semantic (Qdrant similarity) caching of prior answers - Per-IP rate limiting (`slowapi` + Redis) on the chat endpoint **Observability** - Full request tracing via LangSmith — retrieval, cache lookups, and generation are each independently traced **Engineering** - Async FastAPI + async SQLAlchemy 2.0 (typed `Mapped`/`mapped_column` models) - Alembic-managed database migrations - Dependency-injected DB sessions - Integration test suite (`pytest` + `httpx`) - Fully containerized (Docker + Docker Compose: API, Postgres, Qdrant, Redis) - CI pipeline (GitHub Actions) ## Tech stack | Layer | Choice | |---|---| | API framework | FastAPI (async) | | Database | PostgreSQL + SQLAlchemy 2.0 + Alembic | | Vector store | Qdrant | | Cache / rate limiting | Redis | | Embeddings | sentence-transformers (BAAI/bge-small-en-v1.5) | | LLM | Ollama (local, free) | | Observability | LangSmith | | Dependency management | uv | | Testing | pytest, httpx | | Containerization | Docker, Docker Compose | | CI | GitHub Actions | ## Getting started ```bash git clone https://github.com/<your-username>/<repo-name>.git cd <repo-name> cp .env.example .env # fill in your values docker compose up -d --build ``` Once running, visit `http://localhost:8000/docs` for the interactive API documentation. **Upload a document:** ```bash curl -X POST http://localhost:8000/documents/ -F "file=@your-file.pdf" ``` **Ask a question:** ```bash curl -X POST http://localhost:8000/chat/ -H "Content-Type: application/json" \ -d '{"question": "What is your return policy?"}' ``` **Embed the widget on any website:** ```html <script src="https://your-deployment.com/widget.js"></script>

          
## Running tests

```bash
uv run pytest -v

app/
  main.py               # App assembly, middleware, exception handlers
  core/                 # Config, database, rate limiter
  models/               # SQLAlchemy models
  schemas/              # Pydantic request/response contracts
  guardrails/           # Prompt injection defense, PII detection
  services/             # Embeddings, vector store, document processing, cache
  api/                  # Route handlers (documents, chat, health)
widget/
  widget.js             # Embeddable Shadow-DOM-isolated chat widget
tests/                  # Integration test suite
alembic/                # Database migrations
docker-compose.yml
Dockerfile

Roadmap
 Agentic self-correcting retrieval (grade → rewrite → re-retrieve loop)
 Tool-calling for live business data (order status, inventory lookups)
 Human escalation workflow with email handoff
 Admin dashboard for document management

License

MIT
