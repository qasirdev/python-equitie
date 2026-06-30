# EquiTie Prototype Walkthrough Script

**[0:00 - 0:30] Introduction**
"Hello, this is a walkthrough of the EquiTie AI Portfolio Assistant prototype. We built this strictly focusing on financial accuracy, determinism, and robust AI orchestration."

**[0:30 - 1:15] Architecture & Guardrails**
"We used a Next.js frontend connecting to a FastAPI backend. To guarantee zero hallucinated math, we strictly use deterministic Python tools built with Pandas to calculate MOIC, distributions, and fees. The LLM only acts as a narrator of these pre-calculated facts. Security-wise, our PromptInjectionDetector blocks any non-financial or out-of-scope queries."

**[1:15 - 2:00] Live Demo**
"Let's see it in action. In the UI, we select an investor. We ask: 'What is my current MOIC?' The agent triggers the `get_portfolio_overview` tool, and the backend returns the precise metric calculated from the CSVs. Notice the Observability Badge rendering real-time token usage, latency, and explicit tool invocations."

**[2:00 - 2:30] Personalisation & Scale**
"Based on the investor's profile, the agent’s tone is tailored. For a highly sophisticated investor, the tone is data-dense. For a less tech-savvy investor, the tone automatically shifts to explain jargon in plain language. Finally, while we use in-memory DataFrames for this sprint, our roadmap details how this scales to a full production architecture."
