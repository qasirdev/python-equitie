# EquiTie — AI-Powered Investor Portfolio Assistant

> **A production-grade, agentic AI system for querying private-equity portfolio data via natural language.**
> Built with FastAPI · Next.js 19 · OpenAI Function Calling · Pandas · Docker · Vercel

[![CI](https://github.com/qasirdev/python-equitie/actions/workflows/ci.yml/badge.svg)](https://github.com/qasirdev/python-equitie/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15%2B-black?logo=next.js)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![uv](https://img.shields.io/badge/package%20manager-uv-purple)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/linting-ruff-red)](https://github.com/astral-sh/ruff)
[![Mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](https://mypy-lang.org/)

---

## 📽️ Demo

> Watch the prototype in action:

**[▶ Click here to view the full demo recording](https://github.com/qasirdev/python-equitie/raw/main/docs/guidence/equitie-recording.mov)**

<img width="1656" height="831" alt="EquiTie AI Portfolio Assistant — Chat Interface Screenshot" src="https://github.com/user-attachments/assets/c6678277-80dd-4a61-84ee-2bc55b67c167" />

---

## 🗂️ Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
  - [System Diagram](#system-diagram)
  - [Agent Loop & Tool Orchestration](#agent-loop--tool-orchestration)
  - [Data Layer](#data-layer)
  - [Security Model](#security-model)
  - [Personalisation Engine](#personalisation-engine)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Local Development](#-local-development)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Running with Docker Compose](#running-with-docker-compose)
  - [Running Backend Only](#running-backend-only)
  - [Running Frontend Only](#running-frontend-only)
- [API Reference](#-api-reference)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Code Quality & Tooling](#-code-quality--tooling)
- [Deployment](#-deployment)
- [Design Decisions & Assumptions](#-design-decisions--assumptions)
- [Production Roadmap](#-production-roadmap)
- [Known Limitations](#-known-limitations)
- [Contributing](#-contributing)

---

## 🧭 Overview

**EquiTie** is a senior-level case study demonstrating how to architect a *real-time, streaming AI agent* on top of private-equity portfolio data. Investors interact with a natural-language chat interface to query metrics such as **MOIC**, **DPI**, **RVPI**, capital-call obligations, fee schedules, valuation histories, and realised distributions — all without writing a single line of SQL.

The system enforces a strict **"LLM never computes math"** invariant: all deterministic financial calculations are delegated to Python tools registered on the agent's function-calling interface, while the LLM is used exclusively for language understanding and reasoning.

---

## ✨ Key Features

| Feature | Detail |
|---|---|
| 🤖 **Agentic Reasoning Loop** | GPT-4o / GPT-4o-mini via OpenRouter with capped 5-iteration tool-call loop |
| 📊 **8 Deterministic Finance Tools** | Portfolio overview, single-position drill-down, obligations, fee schedules, valuation history, account statement, realised outcomes, entity resolution |
| 🔒 **Prompt-Injection Guard** | Regex-based injection detector + financial-domain keyword gate on every request |
| 🧑‍💼 **Investor Personalisation** | Age, tech-savviness, sector weighting — tone-adaptive system prompt per investor |
| 📈 **Multi-Currency FX** | Vectorised currency conversion across all portfolio metrics |
| 🌊 **Real-Time SSE Streaming** | `StreamingResponse` with `text/event-stream` — token-by-token delivery to the client |
| 🐳 **Single-Image Docker Stack** | Node frontend builder + Python runtime + Nginx + Supervisor in one container |
| ☁️ **Serverless-Ready** | Mangum ASGI adapter for AWS Lambda / Vercel Serverless Functions |
| ✅ **Full CI/CD** | GitHub Actions: Ruff, Mypy, pip-audit, Pytest, Docker build, and doc checks |
| 🔢 **Strict Type Safety** | 100% Mypy-clean, Pydantic v2 models, NumPy-safe JSON serialisation |

---

## 🏗️ Architecture

### System Diagram

<img width="902" height="601" alt="system_architecture" src="https://github.com/user-attachments/assets/a8a21639-d66b-4802-b6cf-7358b4aa8292" />

---

### Agent Loop & Tool Orchestration

The core agent loop lives in [`backend/agent/runner.py`](backend/agent/runner.py).

**Execution flow:**

1. **Personalisation** — `build_personalisation_profile(investor_id)` enriches the system prompt with investor-specific tone, deal count, and sector weighting before the first LLM call.
2. **Streaming LLM call** — `AsyncOpenAI.chat.completions.create(stream=True, stream_options={"include_usage": True})` yields delta chunks and usage tokens concurrently.
3. **Tool-call accumulation** — Streaming deltas are reassembled into complete tool-call payloads by index.
4. **Cross-tenant guard** — Any `investor_id` inside tool arguments is validated against the session investor; mismatches are blocked and overwritten.
5. **Deterministic Python execution** — `TOOLS_REGISTRY[func_name](**args)` dispatches to a pure Python function; NumPy types are serialised safely via `NumpyEncoder`.
6. **Loop capping** — A maximum of **5 tool-calling iterations** prevents runaway agentic loops.
7. **SSE events** — Each step emits a structured JSON line (`type: content | tool_call | usage | error`) over `text/event-stream`.

```python
# Excerpt: runner.py — SSE event types
{"type": "content",   "token": "<streamed token>"}
{"type": "tool_call", "function": "<name>", "arguments": "<json>"}
{"type": "usage",     "prompt_tokens": 412, "completion_tokens": 87}
{"type": "error",     "message": "<human readable>"}
```

**Registered tools (8):**

| Tool | Inputs | Purpose |
|---|---|---|
| `get_portfolio_overview` | `investor_id` | MOIC, DPI, RVPI, holdings list, committed vs contributed |
| `get_single_position` | `investor_id`, `deal_id` | Deal-level P&L: cost basis, current value, share price delta |
| `get_obligations` | `investor_id` | Overdue management fees + upcoming capital calls |
| `get_realised_outcomes` | `investor_id` | Distributions, exits, net-of-carry amounts |
| `get_fees_schedule` | `investor_id`, `deal_id` | Management fee %, performance fee %, investor discount |
| `get_valuation_history` | `deal_id` | Time-series of share prices per deal |
| `get_account_statement` | `investor_id` | Chronological capital contributions, fees, distributions |
| `resolve_entity` | `query`, `entity_type` | Fuzzy company/deal name resolution |

---

### Data Layer

Located in [`backend/data_layer/`](backend/data_layer/), the data layer is structured as a singleton `DataLoader` loaded once at application startup via FastAPI's `lifespan` context manager.

**10 CSV datasets loaded into memory:**

| File | Description |
|---|---|
| `investors.csv` | Investor profiles: age, tech-savviness, reporting currency |
| `portfolio_companies.csv` | Company master: name, sector, stage |
| `deals.csv` | Deal master: entry share price, round, company link |
| `allocations.csv` | Per-investor deal allocations: units, contributed amount, fees |
| `valuations.csv` | Time-series share prices per deal |
| `capital_calls.csv` | Upcoming capital call obligations |
| `fees.csv` | Management fees with status (overdue / upcoming) |
| `distributions.csv` | Realised distributions and exits |
| `statement_lines.csv` | Full financial account statement lines |
| `fx_rates.csv` | FX rates for multi-currency conversion |

**Metrics engine (`metrics.py`):**

All financial KPIs are calculated via vectorised Pandas operations with FX conversion:

```
MOIC  = (Realised Value + Current Value) / Cost Basis
DPI   = Realised Value / Cost Basis
RVPI  = Current Value / Cost Basis
```

All amounts are normalised to each investor's `reporting_currency` using `convert_currency_vectorized()`.

---

### Security Model

Located in [`backend/security/gate.py`](backend/security/gate.py), the `PromptInjectionDetector` runs on every inbound user message **before** it reaches the agent.

**Two-layer defence:**

1. **Injection pattern matching** — Regex detects `"ignore all previous instructions"`, `"you are now"`, `"bypass"`, `"system prompt"`, and similar jailbreak patterns. Any match raises HTTP 400.
2. **Domain enforcement** — Queries longer than 3 words are checked for intersection with a financial keyword set (`portfolio`, `MOIC`, `DPI`, `valuation`, `capital`, `fund`, etc.). Off-topic queries (e.g. *"What is the capital of France?"*) are rejected with HTTP 400.

> **Production note:** The domain-enforcement heuristic is designed to be replaced by an embedding-based classifier or a lightweight LLM intent-classification step for higher accuracy.

---

### Personalisation Engine

Located in [`backend/data_layer/personalisation.py`](backend/data_layer/personalisation.py), the engine builds a per-investor context profile before each agent call:

| Signal | Source | Usage |
|---|---|---|
| `age` | `investors.csv` | Adaptive tone (plain language vs technical) |
| `tech_savviness` | `investors.csv` | Controls jargon density (MOIC, Carry, TVPI vs explanations) |
| `deal_count` | Derived from allocations | Contextualises response depth |
| `top_sectors` | Derived from deals + companies | Sector-aware commentary |

Three tone modes: **data-dense** (high tech-savviness), **respectful & plain** (older, low tech-savviness), **professional & balanced** (default).

---

## 🧰 Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Backend Runtime** | Python | 3.12+ | Core language |
| **Web Framework** | FastAPI | ≥0.111 | Async API, SSE streaming, OpenAPI docs |
| **ASGI Server** | Uvicorn | ≥0.30 | Production-grade ASGI server |
| **Package Manager** | uv (Astral) | latest | Fast, lock-file-based dependency management |
| **LLM Client** | openai | ≥2.44 | AsyncOpenAI with streaming + function calling |
| **Data Processing** | Pandas | ≥2.2 | In-memory data layer, vectorised operations |
| **Settings** | pydantic-settings | ≥2.3 | Typed environment configuration |
| **Logging** | structlog | ≥24.1 | Structured JSON logging |
| **Serverless Adapter** | Mangum | ≥0.17 | AWS Lambda / Vercel ASGI adapter |
| **Frontend Framework** | Next.js | 15+ | React 19 chat UI, SSE consumer |
| **Frontend Language** | TypeScript | 5+ | Type-safe React components |
| **Containerisation** | Docker + Compose | — | Multi-stage build (Node → Python) |
| **Reverse Proxy** | Nginx | — | Static file serving + API proxy |
| **Process Manager** | Supervisor | — | Multi-process management in container |
| **Linter/Formatter** | Ruff | ≥0.4 | PEP 8 enforcement + import sorting |
| **Type Checker** | Mypy | ≥1.10 | Static type analysis |
| **Testing** | Pytest + pytest-asyncio | ≥8.2 / ≥0.23 | Async test support |
| **HTTP Test Client** | HTTPX | ≥0.27 | Async FastAPI test client |
| **Security Audit** | pip-audit | — | Dependency vulnerability scanning |
| **Pre-commit** | pre-commit | ≥3.7 | Git hook enforcement |
| **Build Backend** | Hatchling | — | PEP 517 compliant wheel builder |

---

## 📁 Project Structure

```
python-equitie/
├── backend/                        # FastAPI application
│   ├── main.py                     # App factory: lifespan, CORS, routers, exception handlers
│   ├── settings.py                 # Pydantic-settings typed config (CORS, env, etc.)
│   ├── logging_config.py           # structlog JSON logging setup
│   ├── agent/
│   │   ├── runner.py               # Core agentic loop: streaming LLM ↔ tool execution
│   │   ├── tools.py                # 8 deterministic finance tools + OpenAI tool schemas
│   │   └── prompt.py               # System prompt factory with personalisation injection
│   ├── api/
│   │   └── router.py               # REST endpoints: /health, /investors, /chat (SSE)
│   ├── data_layer/
│   │   ├── loader.py               # DataLoader singleton: 10 × CSV → Pandas DataFrames
│   │   ├── metrics.py              # MOIC, DPI, RVPI calculation (vectorised, FX-aware)
│   │   ├── personalisation.py      # Investor tone & context profile builder
│   │   ├── fx.py                   # Vectorised multi-currency FX conversion
│   │   ├── fees.py                 # Fee calculation helpers
│   │   └── schemas.py              # Pydantic data schemas
│   ├── security/
│   │   └── gate.py                 # PromptInjectionDetector: regex + domain guard
│   └── tests/                      # Pytest test suite (async)
├── frontend/                       # Next.js 15 / React 19 chat UI
│   ├── app/                        # App Router pages
│   ├── components/                 # Chat UI components
│   └── package.json
├── data/                           # 10 × synthetic CSV datasets
├── docs/                           # Execution rules, task tracking, demo assets
├── scripts/
│   └── start.sh                    # Convenience launcher (Docker Compose)
├── .github/
│   └── workflows/ci.yml            # GitHub Actions CI pipeline
├── .pre-commit-config.yaml         # Pre-commit hooks (Ruff format + check)
├── Dockerfile                      # Multi-stage: Node (frontend) → Python (runtime)
├── docker-compose.yml              # Full-stack local orchestration
├── nginx.conf                      # Nginx: static files + /api/* proxy
├── supervisord.conf                # Supervisor: Nginx + Uvicorn process management
├── vercel.json                     # Vercel serverless deployment config
├── pyproject.toml                  # PEP 517 project config, Ruff, Mypy, dependencies
├── uv.lock                         # Locked dependency manifest
├── AGENT.md                        # AI agent workflow rules and coding standards
└── README.md
```

---

## 💻 Local Development

### Prerequisites

| Tool | Version | Installation |
|---|---|---|
| `uv` | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `docker` | 24+ | [docs.docker.com](https://docs.docker.com/get-docker/) |
| `docker compose` | v2 | Bundled with Docker Desktop |
| `node` | 20 LTS | [nodejs.org](https://nodejs.org/) |

### Environment Variables

Copy the example file and populate it:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ (or OpenRouter) | OpenAI API key for GPT-4o / GPT-4o-mini |
| `OPENROUTER_API_KEY` | Optional | Alternative: OpenRouter key |
| `OPENAI_BASE_URL` | Optional | Override LLM base URL (e.g. `https://openrouter.ai/api/v1`) |
| `LLM_MODEL` | Optional | Model name override (default: `gpt-4o-mini`) |
| `LLM_OPENROUTER_MODELS` | Optional | OpenRouter model slug (highest priority) |
| `CORS_ORIGINS` | Optional | Comma-separated allowed origins |
| `ENVIRONMENT` | Optional | `development` or `production` |

### Running with Docker Compose

The recommended way to run the full stack (frontend + backend + Nginx):

```bash
# 1. Ensure .env is populated
cp .env.example .env && nano .env

# 2. Start the stack
./scripts/start.sh
# OR directly:
docker compose up --build

# 3. Access the application
open http://localhost
```

Health check endpoint: `GET http://localhost/api/v1/health` → `{"status": "ok"}`

### Running Backend Only

Ideal for API development with hot-reload:

```bash
# Install dependencies
uv sync

# Start the backend
uv run uvicorn backend.main:app --reload --port 8000

# API available at:
open http://localhost:8000/docs   # Swagger UI
open http://localhost:8000/redoc  # ReDoc
```

### Running Frontend Only

```bash
cd frontend
npm install
npm run dev
# Available at http://localhost:3000
```

> **Note:** Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` when running the frontend independently.

---

## 📡 API Reference

Base path: `/api/v1`

### `GET /health`

Health check.

**Response:**
```json
{"status": "ok"}
```

---

### `GET /investors`

Returns all available investors for the UI dropdown.

**Response:**
```json
[
  {"investor_id": "INV-001", "investor_name": "Alice Chen"},
  {"investor_id": "INV-002", "investor_name": "Robert Kane"}
]
```

---

### `POST /chat`

Runs the agentic loop and streams the response as Server-Sent Events.

**Request body:**
```json
{
  "investor_id": "INV-001",
  "messages": [
    {"role": "user", "content": "What is my current MOIC?"}
  ]
}
```

**Streaming response** (`Content-Type: text/event-stream`):

Each line is a newline-delimited JSON event:

```jsonl
{"type": "tool_call", "function": "get_portfolio_overview", "arguments": "{\"investor_id\": \"INV-001\"}"}
{"type": "content", "token": "Your current"}
{"type": "content", "token": " MOIC is **2.3×**"}
{"type": "usage", "prompt_tokens": 412, "completion_tokens": 87}
```

**Error events:**
```jsonl
{"type": "error", "message": "Reached maximum reasoning steps."}
```

**Security rejections:** HTTP `400` with `{"detail": "Query violates security policies."}` or `{"detail": "Query must be related to your portfolio or investments."}`

---

## ⚙️ CI/CD Pipeline

Pipeline defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — runs on all pull requests and pushes to `epic/autonomus-implementation`.

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions CI                     │
├─────────────┬──────────────────────────┬────────────────┤
│  backend    │       frontend           │    docker      │
│             │                          │                │
│ uv sync     │ npm ci                   │ (needs both)   │
│ ruff format │ npm run lint             │                │
│ ruff check  │ npm run test             │ docker compose │
│ mypy        │ npm run build            │ build app      │
│ pip-audit   │                          │                │
│ pytest      │                          │                │
└─────────────┴──────────────────────────┴────────────────┘
                                          │
                               workflow-docs job
                               (validates task tracking docs exist)
```

All backend quality gates are **blocking**. The `pip-audit` step is non-blocking during the prototype phase (allows CI to continue on audit failure).

---

## 🧹 Code Quality & Tooling

Run all checks locally before pushing:

```bash
# Format check
uv run ruff format backend

# Lint
uv run ruff check backend

# Type check
uv run mypy backend

# Tests
uv run pytest backend -v

# Security audit
uv tool run pip-audit

# All in one (matches CI)
uv run ruff check backend && uv run ruff format backend && uv run mypy backend && uv run pytest backend
```

Pre-commit hooks run automatically on `git commit`:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files
```

**Code standards:**
- Line length: **88** (Black-compatible)
- Target Python: **3.12**
- Ruff rule sets: `E` (pycodestyle), `F` (pyflakes), `I` (isort)
- Mypy: `ignore_missing_imports = true`, all untyped library stubs excluded

---

## 🚀 Deployment

### Docker (Self-Hosted / Cloud VM)

```bash
docker compose up --build -d
```

The image serves both the static Next.js export (via Nginx) and the FastAPI backend, managed by Supervisor.

### Vercel (Serverless)

```bash
vercel --prod
```

The `vercel.json` routes `/api/*` to the Mangum-wrapped FastAPI handler. The `mangum` package wraps the ASGI app for AWS Lambda-compatible serverless runtimes.

### Environment Promotion

| Environment | LLM Model | Data Layer | Notes |
|---|---|---|---|
| Development | `gpt-4o-mini` | CSV in-memory | Hot-reload, debug logging |
| Staging | `gpt-4o-mini` | CSV in-memory | CI-validated Docker image |
| Production (roadmap) | `gpt-4o` | PostgreSQL | Persistent data, auth, observability |

---

## 🧠 Design Decisions & Assumptions

### Architectural Decisions

| Decision | Rationale |
|---|---|
| **LLM never computes math** | Deterministic financial KPIs (MOIC, DPI, RVPI) are computed in Python using vectorised Pandas. The LLM only interprets and communicates results, eliminating hallucination risk on numerical outputs. |
| **OpenAI Function Calling (strict mode)** | Enforces structured tool dispatch. No JSON parsing from free-form text. Arguments are validated before execution. |
| **Async streaming (SSE)** | Delivers first tokens immediately, improving perceived latency for investors. The agent's reasoning chain is visible in real-time via `tool_call` events. |
| **Singleton DataLoader** | CSVs are loaded once at startup via FastAPI `lifespan`. Eliminates per-request I/O overhead at the cost of memory footprint. |
| **uv for dependency management** | 10–100× faster than pip, fully reproducible via `uv.lock`, native PEP 517/518 support. |
| **Multi-stage Docker build** | Separates Node build artifacts from the Python runtime image, minimising final image size. |
| **structlog** | Structured JSON logging enables log aggregation (Datadog, CloudWatch, Loki) without format changes in production. |
| **Mangum adapter** | Zero-code change required to deploy the same FastAPI app as a serverless function. |

### Assumptions

- The 10 provided CSV files fit entirely in memory (prototype scope).
- Financial reporting reference date is anchored to **June 25, 2026** for determining overdue vs upcoming fee/call status.
- Investor authentication is implicit — the selected `investor_id` from the UI dropdown is trusted as the authenticated session identity.
- All LLM interactions are scoped to a single investor; cross-investor data access is blocked at the tool-execution layer.

---

## 🗺️ Production Roadmap

The following gaps are acknowledged as out-of-scope for the prototype and are detailed in [`proposal-production-saas.md`](proposal-production-saas.md):

| Priority | Gap | Solution |
|---|---|---|
| 🔴 Critical | In-memory data | Migrate to PostgreSQL with SQLAlchemy async ORM |
| 🔴 Critical | Implicit auth | Auth0 / Cognito JWT + RBAC middleware |
| 🟡 High | LLM observability | LangSmith / OpenTelemetry tracing per agent loop |
| 🟡 High | Domain enforcement | Replace regex with embedding-based intent classifier |
| 🟡 High | Concurrent writes | Transactional state management for document signing, mutations |
| 🟢 Medium | Model fallback | Primary/fallback model routing via OpenRouter |
| 🟢 Medium | Response caching | Redis cache layer for repeated portfolio queries |
| 🟢 Medium | Rate limiting | Per-investor token-bucket rate limiting on `/chat` |
| 🟢 Medium | Audit logging | Immutable event log of all investor queries and tool calls |
| ⬜ Low | Async tools | Async `TOOLS_REGISTRY` for I/O-bound tool execution |

---

## ⚠️ Known Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **In-Memory Data** | Not suitable for datasets exceeding available RAM; no durability | Migrate to PostgreSQL (see roadmap) |
| **Read-Only** | No mutation support — signing documents, updating allocations require transactional state management | Phase 2 scope |
| **Implicit Auth** | `investor_id` is passed from the client; no JWT validation | Blocked by cross-tenant guard at the tool layer; full auth in roadmap |
| **Synchronous Tools** | Tool functions are synchronous; blocking event loop under high concurrency | Wrap with `asyncio.to_thread()` or rewrite as async |
| **Single-Container Deploy** | Nginx + Uvicorn + Supervisor colocated limits horizontal scalability | Separate services for production |
| **Prototype Model** | `gpt-4o-mini` may hallucinate on edge-case financial reasoning | Use `gpt-4o` with `temperature=0` for production financial use cases |

---

## 🤝 Contributing

This project follows the **5-agent handoff workflow** defined in [`AGENT.md`](AGENT.md):

```
Coding → Refactor → PR Code Review → Testing → Docs
```

1. Fork the repository and create a feature branch.
2. Run all quality gates before opening a PR:
   ```bash
   uv run ruff check backend && uv run ruff format backend && uv run mypy backend && uv run pytest backend
   ```
3. Follow the PR template at [`.github/pull_request_template.md`](.github/pull_request_template.md).
4. All PRs are validated by the automated CI pipeline before merge.

---

<div align="center">

**Built by [Qasir Mehmood](https://github.com/qasirdev) · Senior Software Engineer · 2026**

*FastAPI · Next.js · OpenAI · Pandas · Docker · Vercel*

</div>
