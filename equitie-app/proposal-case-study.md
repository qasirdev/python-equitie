# Proposal: EquiTie Investor Assistant (Case Study Prototype)

**Objective**: Build a narrow, highly accurate, and personalised conversational AI assistant for EquiTie investors to query their portfolio data, strictly within a 2-3 hour timebox.

This proposal is designed to explicitly maximise the score against the **EquiTie Evaluation Rubric**, prioritising reliability, product judgment, and clean technical architecture over over-engineering or premature scaling.

---

## 1. Scope and Capabilities (Product Judgment - 15%)

The prototype will be deliberately **narrow and deep**, focusing exclusively on the required feature set:
*   **Portfolio Overview**: Holdings, current value, total committed vs. contributed, and MOIC.
*   **Position Deep-Dives**: Current value, cost basis, entry share price (handling multi-round SPVs).
*   **Obligations & Outcomes**: Upcoming capital calls, overdue management fees, exits, and net distributions.
*   **Personalisation**: 
    *   **Tone & Depth**: Plain language with jargon explanations (e.g., MOIC, Carry) for older/less tech-savvy investors. Data-dense and concise answers for highly sophisticated investors.
    *   **Contextual Framing**: Answers will dynamically highlight the investor's most active sectors or deal count to make the interaction feel truly bespoke.

## 2. Technical Architecture (Technical Architecture - 10%)

To ensure a clean separation of concerns and rapid shipping within the timebox, the architecture will be structured as follows:

*   **Frontend**: Next.js 16 (App Router) + Tailwind CSS. A simple but polished chat interface with server-sent events (SSE) for streaming responses.
*   **Backend**: FastAPI (Python 3.12). Exposes the chat streaming endpoint and handles the agent orchestration loop.
*   **Data Layer**: In-memory `pandas` DataFrames. The 10 provided CSV files will be loaded into memory at application startup. This avoids the overhead of setting up a PostgreSQL/vector database, perfectly fitting the 3-hour timebox.
*   **LLM Integration**: `openai/gpt-oss-120b` (or equivalent strong reasoning model) routed via OpenRouter for function-calling. 

## 3. Reliability & Verification (Reliability & Verification - 20%)

**The most critical constraint: The LLM will NEVER perform financial math.**

1.  **Deterministic Tooling**: The backend will expose 9 strict Python tools (e.g., `compute_moic`, `get_capital_calls`, `resolve_investor`) to the LLM via OpenAI function calling schemas. 
2.  **Pandas Execution**: All calculations (FX conversion, fee discounts, net distribution math) will be executed by deterministic Python/Pandas code querying the CSV data.
3.  **LLM as a Narrator**: The LLM will only receive the JSON output from these tools and will be instructed to *narrate* the results, strictly citing the source rows without hallucinating calculations.
4.  **Edge Case Handling**: Explicit Python logic will handle the 13 deliberate traps in the dataset (e.g., multi-round companies, share-price discounts, down-rounds, write-offs).

## 4. AI-Native Workflow & Speed (AI Workflow - 20%, Speed - 5%)

*   **Development Speed**: The prototype will be built using advanced agentic tools with a highly structured workflow (YOLO mode with sequential Coding → Refactoring → Critic/Review → Testing → Documentation agents).
*   **Testing**: Automated `pytest` suites will be generated to spot-check known ground-truth values from the CSVs (e.g., ensuring a specific investor's MOIC matches manual calculation).

## 5. Deliverables & Communication (Communication - 10%, Roadmap - 20%)

By the end of the timebox, the following will be delivered:
1.  **Working Prototype**: A Next.js/FastAPI application orchestratable via Docker.
2.  **README**: Clear setup instructions, architectural decisions, and known limitations (e.g., in-memory data scale limits).
3.  **ai-workflow.md**: Transparent documentation of the AI tools used, rejection rationale, and verification strategies.
4.  **roadmap.md**: A distinct 6-month plan mapping the transition from this prototype to a full production SaaS platform.
