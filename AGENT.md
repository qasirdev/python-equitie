# EquiTie AI Portfolio Assistant

## Workflow Rules
- **Reference Architectures**: You MUST refer to `../../daily-briefing` and `../../job-discovery` whenever making technical decisions or setting up infrastructure.
- **5-Agent Handoff**: Coding -> Refactor -> PR Code Review -> Testing -> Docs
- **Review Agent**: This file `.agent/rules/review.mdc` acts as your PR Code Review Agent. Whenever the coding or refactor agents finish a task, this Review agent will now automatically trigger to audit the diff for complexity, security, and architectural violations before the task is marked as "Done".
- **YOLO Mode**: Do not pause for feedback unless completely blocked.
- **Strict Architecture**: LLM never computes math.

See `docs/EXECUTION-RULES.md` for full execution protocols.
