# EquiTie AI Portfolio Assistant

The EquiTie AI Portfolio Assistant is a unified monorepo for querying investor portfolio data through an AI agent.

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
