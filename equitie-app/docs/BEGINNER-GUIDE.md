# Beginner Guide

Welcome to the EquiTie AI Portfolio Assistant.

## Local Development
We use `docker-compose` to run the stack.
```bash
./scripts/start.sh
```
This runs Nginx, FastAPI, and the Next.js static build via Supervisord.

## Tech Stack
- **FastAPI**: Backend REST API.
- **Next.js**: Frontend UI.
- **Docker**: Local containerization.
- **Vercel**: Production serverless environment.
