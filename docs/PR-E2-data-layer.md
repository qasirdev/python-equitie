# Pull Request: Epic E2 - Data Layer Implementation

## Description
This Pull Request implements the core Data Layer for the EquiTie AI Portfolio Assistant (Epic E2). The module is designed to cleanly ingest and transform synthetic portfolio data into structured, strictly typed representations, strictly adhering to AI safety rules (offloading all deterministic financial math from the LLM).

## Key Architectural Decisions & Engineering Practices
- **Data Ingestion & Lifecycle Management**: Implemented `DataLoader` as a singleton managed by the FastAPI `lifespan` context manager, ensuring all 10 CSV dataframes are loaded into memory exactly once at application startup.
- **Strict Data Validation**: Engineered comprehensive data schemas using **Pydantic v2** (`ConfigDict(strict=True)`), enforcing rigorous type safety across the data pipeline.
- **High-Performance Vectorization**: Completely eliminated iterative Pandas operations (`.iterrows()`, `.apply(axis=1)`). Refactored the FX and Metrics modules to utilize fully vectorized operations (`pandas.Series.map`, broadcast arithmetic, and `pandas.merge`), achieving highly performant and deterministic financial calculations (MOIC, DPI, RVPI, TVPI).
- **Edge Case Coverage**: Correctly mapped and tested complex domain-specific edge cases, including:
  - Consolidating multi-round investments (SPVs) by grouping via `deal_id`.
  - Determining Current Value deterministically using the latest sorted valuation mark, seamlessly handling down-rounds and write-offs.
  - Dynamically applying per-investor fee discounts and structuring effective fee percentages.
- **Strict Cross-Tenant Data Isolation**: Implemented data segregation at the data-frame level, guaranteeing that metric and personalisation endpoints restrict visibility exclusively to the queried `investor_id`.
- **Quality Assurance**: Integrated robust, automated unit testing via **pytest** and enforced formatting/type checking via **mypy** and **ruff** in adherence to the `.agent/rules/review.mdc` rubric.

## Technical Stack & ATS Keywords
`Python 3.12+`, `Pandas`, `Vectorization`, `Data Engineering`, `FastAPI`, `Pydantic v2`, `Pytest`, `Type Hinting (mypy)`, `Software Architecture`, `Deterministic Algorithms`, `Cross-Tenant Security`, `FinTech`, `Metrics (MOIC, DPI, RVPI)`.

## Verification Checklist
- [x] All 10 Pandas DataFrames load flawlessly upon FastAPI startup.
- [x] Strict Pydantic models cover all entities (Investors, Deals, Allocations, Valuations, etc.).
- [x] Currency conversion is fully vectorized and leverages the `fx_rates` dimension correctly.
- [x] All deterministic logic runs independently (LLM never computes math).
- [x] Personalisation profiles correctly ingest age, tech savviness, and portfolio depth to generate dynamic LLM prompts.
- [x] Test coverage via `pytest backend/tests/test_data_layer.py` passes 100%.
- [x] Code conforms strictly to `mypy` and `ruff` linting standards.
