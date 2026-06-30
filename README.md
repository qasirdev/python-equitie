# EquiTie AI Portfolio Assistant

The EquiTie AI Portfolio Assistant is a unified monorepo for querying investor portfolio data through an AI agent.

## Demo
Watch the prototype in action:

<video src="./docs/guidence/equitie-recording.mov" width="100%" controls autoplay loop muted></video>

## Architecture

- **Backend**: FastAPI (Python 3.12+) acting as the agent orchestration layer.
- **Frontend**: Next.js (TypeScript/React 19) providing a chat-based user interface.
- **Data Layer**: In-memory Pandas DataFrames, directly loaded from CSVs.
- **Deployment**: Vercel Serverless (using Mangum) / Docker locally.

## Setup & Running Locally

1. Create your `.env` file from `.env.example`.
2. Ensure you have `uv` and `docker` installed.
3. Start the entire stack via Docker Compose:
   ```bash
   ./scripts/start.sh
   ```

## Development

- Always run verification checks before pushing backend code:
  ```bash
  uv run ruff check backend && uv run ruff format backend && uv run mypy backend
  ```

For full context and developer rules, refer to `AGENT.md`.

## Models Used
- We utilize `openai/gpt-4o-mini` (or standard `gpt-4o`) via OpenRouter or native OpenAI API as the reasoning agent.
- Function Calling (Tools) is strictly enforced to offload any deterministic financial calculations to Python.

## Assumptions
- The 10 provided CSV files fit entirely in memory.
- The user is considered implicitly authenticated once an investor is selected in the UI dropdown.
- Financial reporting dates are anchored to June 25, 2026, for determining upcoming vs overdue fees.

## Limitations
- **In-Memory Data**: Loading all Pandas DataFrames into memory works for this prototype but requires migration to a relational DB (e.g., PostgreSQL) for scale.
- **Concurrent Writes**: The application is currently read-only for investor queries; mutations (like signing documents) would require transactional state management.
