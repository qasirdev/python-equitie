# Kick-off Prompt — EquiTie AI Portfolio Assistant

**Version:** 1.0.0 | **Last Updated:** June 2026

This document contains the ready-to-use prompt to start autonomous implementation of the EquiTie AI Portfolio Assistant.

---

## Pre-Flight Checklist

Before running the kick-off prompt, verify:

- [ ] All documentation files are present in `equitie-app/`
- [ ] `docs/jira-tickets-json/` contains 4 epic JSON files (EQ-E1 through EQ-E4)
- [ ] `docs/tasks/todo.md` exists and is ready for updates
- [ ] `docs/tasks/lessons.md` exists with initial structure
- [ ] `.agent/rules/` contains all rule files (coding, testing, refactor, docs)

---

## Kick-off Prompt (Copy This)

```
You are implementing the EquiTie AI Portfolio Assistant project from scratch.

## CRITICAL: Read These Files First (In Order)
1. AGENT.md — Root index with workflow rules
2. docs/TOKEN-EFFICIENCY.md — Context window rules (read before this file on continuation sessions)
3. docs/EXECUTION-RULES.md — Execution discipline and context management
4. docs/tasks/todo.md — Current task list
5. proposal-case-study.md — The implementation proposal
6. .agent/rules/* — All cursor rules for coding, testing, refactor, and docs

## Project Overview
- FastAPI (backend) + Next.js (frontend) architecture
- Docker local development with Vercel Python Serverless production
- In-memory pandas data layer (strictly no LLM math)
- Deterministic RAG querying 10 CSV files

## Your Mission
Implement Epic EQ-E1 (Project Scaffold & Infrastructure) following the YOLO mode workflow:

### Workflow
0. Run environment checks: Verify uv, npm, docker. Fail fast if missing.
1. Read all tasks from `docs/jira-tickets-json/EQ-E1-scaffold.json`
2. Update `docs/tasks/todo.md` with your implementation plan
3. Implement each task following IMPLEMENTATION DETAILS and EDGE CASES. 
4. After coding: run Refactor Agent checks
5. After refactor: trigger the PR Code Review Agent (`.agent/rules/review.mdc`). This file acts as your PR Code Review Agent. Whenever the coding or refactor agents finish a task, this Review agent will now automatically trigger to audit the diff for complexity, security, and architectural violations before the task is marked as "Done".
6. After review: run Testing Agent checks and VERIFY the test suite passes
7. After testing: run Docs Agent updates

### Rules
- Always use a `<thought>` block to plan your file modifications.
- CRITICAL: Whenever making technical decisions, setting up infrastructure, or defining coding standards, you MUST reference the architectures and patterns in `../../daily-briefing` and `../../job-discovery`.
- Every LLM interaction must rely on deterministic tool returns.
- Pydantic v2 with strict=True for all schemas.

## Start Now
Begin with EQ-001: Monorepo Init with Root AGENT.md
Read the task details from `docs/jira-tickets-json/EQ-E1-scaffold.json`
```
