# Embeddable RAG Ask-Widget

A self-hosted, embeddable AI support widget that businesses can drop into their website with a single script tag. It answers customer questions using Retrieval-Augmented Generation (RAG) grounded in the business's own documents — with guardrails, caching, and observability built in as first-class concerns, not afterthoughts.

Unlike SaaS chat-widget products, this is designed to be **self-hosted**: a business clones/deploys this backend themselves, uploads their own documents, and owns their own data end-to-end.

## Why this exists

Most "AI chatbot for your website" tools are black boxes — you don't know what they retrieve, whether they hallucinate, or where your data goes. This project takes the opposite approach: every stage of the pipeline (retrieval, generation, caching, safety checks) is explicit, inspectable, and traced.

## Architecture

                             Client's Website
                               |
                    <script src="widget.js">
                               |
                               v
                    +-----------------------+
                    |   FastAPI Backend      |
                    |   (this repo)          |
                    +-----------------------+
                       |        |         |
            -----------+        |         +-----------
            |                   |                     |
            v                   v                     v
      +-----------+       +-----------+         +-----------+
      | Postgres  |       |  Qdrant   |         |   Redis   |
      | (doc      |       | (vector   |         | (exact-   |
      | metadata) |       |  search + |         |  match    |
      |           |       |  semantic |         |  cache +  |
      |           |       |  cache)   |         |  rate     |
      |           |       |           |         |  limiting)|
      +-----------+       +-----------+         +-----------+


                    Chat Request Flow (in order)
                    ----------------------------
      1. Prompt injection screen   (input guardrail)
      2. PII redaction             (email/phone/card patterns)
      3. Semantic cache lookup     (Qdrant - skip if hit)
      4. Embed the question        (sentence-transformers)
      5. Retrieve relevant chunks  (Qdrant, score-thresholded)
      6. No-hallucination check    (refuse if no relevant context)
      7. Generate answer           (Ollama, local LLM)
      8. Cache + trace result      (Redis + Qdrant + LangSmith)


                    Document Upload Flow (in order)
                    --------------------------------
      1. Validate file (type + size)
      2. Save metadata to Postgres (status: "processing")
      3. Return immediately to client
      4. [Background] Extract text (pypdf / plain text)
      5. [Background] Recursive chunking
      6. [Background] Embed chunks (sentence-transformers)
      7. [Background] Store vectors in Qdrant
      8. [Background] Update Postgres (status: "ready" / "failed")


                         Observability
                         -------------
              Every retrieval, cache lookup, and
              generation call is traced to LangSmith
          
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
