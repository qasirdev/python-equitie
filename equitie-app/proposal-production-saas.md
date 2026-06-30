# Proposal: EquiTie Investor Assistant (Production SaaS Roadmap)

**Objective**: A 6-month plan to evolve the prototype into a fully integrated, scalable, and proactive Relationship Manager (RM) Bot embedded within the EquiTie iOS investor app.

---

## 1. Scope and Capabilities

The production SaaS product will move beyond passive Q&A to become an active, proactive financial agent:
*   **Proactive Nudges**: Push notifications for upcoming capital calls, overdue management fees, and newly available distributions.
*   **Operational Execution**: Initiate and track KYC/AML refreshes, document requests (e.g., W-9 updates), and onboarding workflows.
*   **Custom Reporting**: Generate and email dynamic, on-demand PDF account statements or tax-time summaries.
*   **Human-in-the-Loop (HITL)**: Seamless escalation to human Relationship Managers for high-risk queries, investment advice, or complex legal disputes.

## 2. Architecture and Tech Stack

A microservices-oriented, highly observable, and fault-tolerant architecture:
*   **Client**: React Native (iOS/Android integration) and Next.js (Web Portal).
*   **API Gateway & Backend**: FastAPI for high-throughput, async REST/SSE endpoints. Traefik or Nginx for API Gateway routing, rate limiting, and CORS.
*   **Orchestration**: **Temporal** (Python SDK) to manage long-running agent workflows (e.g., multi-step document retrieval or KYC approval workflows).
*   **Data Layer**: PostgreSQL for transactional data; Redis for rate limiting and session caching. `pgvector` for vector storage of unstructured fund documents.
*   **Model Hosting**: OpenRouter or Azure OpenAI (provisioned throughput) ensuring SOC2/GDPR compliance and strict data residency.
*   **Observability**: OpenTelemetry + Prometheus/Grafana (metrics) + Loki (logs) + Langfuse (LLM trace observability).

## 3. Data and Integrations

To function as a true RM, the bot will integrate with core enterprise systems:
*   **Portfolio Ledger**: APIs to Investran, eFront, or Allvue for real-time commitment, contribution, and fee data.
*   **CRM**: Salesforce Financial Services Cloud to sync interaction histories and trigger human RM escalations.
*   **KYC/AML**: Onfido or Alloy for identity verification workflows.
*   **E-Signature & Comms**: DocuSign/HelloSign for execution; SendGrid/Twilio for out-of-band communications.
*   **Market Data**: PitchBook or Bloomberg APIs for real-time FX rates and public comparables.

## 4. AI Approach and Safety

Safety and compliance are paramount in venture capital operations:
*   **Strict RAG + Tooling**: The LLM acts purely as an orchestrator and narrator. All financial logic remains in deterministic Python services.
*   **Guardrails Layer**: Implementation of NeMo Guardrails or Llama Guard to detect and block prompt injection, toxic content, and importantly, **unlicensed investment advice**.
*   **PII Redaction**: Presidio (Microsoft) running as middleware to redact PII/NPI before data ever hits external LLM APIs.
*   **Audit Trail**: Every LLM interaction, tool call, and source citation is immutably logged to PostgreSQL for SEC compliance and debugging.

## 5. Team and Hiring (6-Month Plan)

To execute this, an autonomous cross-functional pod is required:
*   **Month 1**: 1x Senior AI/ML Engineer (LLM orchestration, RAG), 1x Senior Backend Engineer (FastAPI, Data pipelines).
*   **Month 2**: 1x Senior Frontend/Mobile Engineer (React Native/Next.js), 1x Product Manager (Domain expert in VC ops).
*   **Month 4**: 1x Platform/DevOps Engineer (Temporal cluster, Kubernetes, Observability).

## 6. Timeline and Phasing

*   **Phase 1 (Months 1-2): Core Data & Read-Only Agent**
    *   Integrate with the portfolio ledger API.
    *   Implement read-only Q&A (scaling the prototype).
    *   Establish observability and security guardrails.
*   **Phase 2 (Months 3-4): Document RAG & Workflow Orchestration**
    *   Deploy Temporal cluster.
    *   Implement semantic search over fund LPAs and quarterly reports (`pgvector`).
*   **Phase 3 (Months 5-6): Proactive Ops & Mobile Integration**
    *   Deploy proactive nudges (capital calls, KYC).
    *   Embed the chat UI natively into the EquiTie iOS app.
    *   SOC2 compliance audit preparation.

## 7. Risks and Cost (Build vs. Buy)

*   **Risk**: LLM Latency & Cost.
    *   *Mitigation*: Route simple queries to fast models (DeepSeek-v4-Flash) and complex routing to larger models. Heavy reliance on caching (Redis/Semantic Cache).
*   **Risk**: Hallucinated Financials.
    *   *Mitigation*: Strict architectural enforcement—LLMs never calculate.
*   **Build vs. Buy**: 
    *   *Buy*: LLM APIs (do not host custom foundation models), E-signature, KYC engines.
    *   *Build*: The agent orchestration layer (Temporal), specific VC data mapping, and the proprietary RAG retrieval strategies.
    *   *Cost Shape*: High upfront engineering OPEX. Variable LLM inference costs scale linearly with MAUs, offset by massive savings in human RM operational hours.
