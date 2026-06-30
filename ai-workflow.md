# EquiTie AI Workflow & Documentation

## Tools & Handoff Strategy Used
This implementation followed the strict 5-Agent Handoff protocol outlined in `AGENT.md`: **Coding -> Refactor -> PR Code Review -> Testing -> Docs**.

**Execution Mode**: YOLO Mode
**Goal**: Rapid implementation of `EQ-E2-data-layer` (6 modules) strictly within the timeframe, enforcing deterministic math constraints.

### 1. Coding Agent (Initial Implementation)
- **Tooling Used**: File writes, `find` for CSV scanning.
- **Actions**:
  - Implemented the `schemas.py` using standard Pydantic models.
  - Implemented `loader.py` to synchronously load 10 Pandas DataFrames into memory at startup.
  - Built out the base logic for `fx.py` (currency conversions), `metrics.py` (MOIC, DPI, RVPI calculations), `fees.py` (discount handling), and `personalisation.py` (persona mapping based on dynamic inputs).

### 2. Refactor & PR Code Review (Critic Agent)
- **Constraints Enforced**: The `.agent/rules/review.mdc` rubric flagged the initial metrics and fx models for iterative Pandas loop inefficiencies (`apply(axis=1)` and `.iterrows()`).
- **Resolution**: Both modules were immediately refactored. `convert_currency_vectorized` was written to perform division and multiplication across the entire Pandas series. Pydantic models were upgraded to enforce `ConfigDict(strict=True)` globally. Missing type hints (`Dict[str, Any]`, `-> None`) were implemented to ensure strict `mypy` compliance.

### 3. Testing Agent
- **Verification Strategy**: Automated unit testing.
- **Implementation**: Created `backend/tests/test_data_layer.py`.
- **Spot-Checks**:
  - **FX Check**: Validated USD conversions and correct rate extractions without hitting division-by-zero errors.
  - **Metrics Calculations**: Ensured strictly numeric properties (no string values or Nulls) were generated for metrics (MOIC >= 0, Cost Basis >= 0).
  - **Isolation**: Handled module-level monkeypatching of the global `data_store` singleton within the `pytest` lifecycle.
- **Result**: `pytest backend/tests/test_data_layer.py` passes 100%.

### 4. Docs Agent
- **Deliverable**: Generated this `ai-workflow.md` documentation file mapping out the internal reasoning loop to fulfill the requirements of the case study proposal.

---

### Known Limitations (For Production Scaling)
- **In-Memory Scale Limits**: Using `loader.py` with in-memory `Pandas DataFrames` is perfect for the 3-hour prototyping timebox, but inherently limits scaling. As outlined in the SaaS roadmap, this layer should be migrated to PostgreSQL and `SQLAlchemy` async ORM to handle millions of statement lines.
