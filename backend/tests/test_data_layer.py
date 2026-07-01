from pathlib import Path

import pandas as pd

from backend.data_layer.loader import DataLoader

# Create a mock data store for tests
mock_data_dir = (
    Path(__file__).parents[2]
    / "EquiTie - Senior Software Engineer - Case Study"
    / "data"
)
loader = DataLoader(str(mock_data_dir))
loader.load_all()

# Patch the global data_store in all modules
import backend.data_layer.loader  # noqa: E402

backend.data_layer.loader.data_store = loader

import backend.data_layer.fx  # noqa: E402

backend.data_layer.fx.data_store = loader  # type: ignore[attr-defined]

import backend.data_layer.metrics  # noqa: E402

backend.data_layer.metrics.data_store = loader  # type: ignore[attr-defined]

import backend.data_layer.fees  # noqa: E402

backend.data_layer.fees.data_store = loader  # type: ignore[attr-defined]

import backend.data_layer.personalisation  # noqa: E402

backend.data_layer.personalisation.data_store = loader  # type: ignore[attr-defined]

from backend.data_layer.fees import calculate_effective_fee  # noqa: E402
from backend.data_layer.fx import (  # noqa: E402
    convert_currency_vectorized,
    get_fx_rate_series,
)
from backend.data_layer.metrics import calculate_investor_metrics  # noqa: E402
from backend.data_layer.personalisation import (  # noqa: E402
    build_personalisation_profile,  # noqa: E402
)


def test_loader_loads_data() -> None:
    assert not loader.investors.empty, "Investors should be loaded"
    assert not loader.fx_rates.empty, "FX rates should be loaded"


def test_fx_conversion() -> None:
    # USD to USD
    amounts = pd.Series([100.0, 200.0])
    from_curr = pd.Series(["USD", "USD"])
    to_curr = pd.Series(["USD", "USD"])
    result = convert_currency_vectorized(amounts, from_curr, to_curr)
    assert result.iloc[0] == 100.0

    # GBP to USD (assuming 1 GBP = some USD)
    gbp_rate = get_fx_rate_series(pd.Series(["GBP"])).iloc[0]
    from_curr = pd.Series(["GBP"])
    to_curr = pd.Series(["USD"])
    result = convert_currency_vectorized(pd.Series([100.0]), from_curr, to_curr)
    assert result.iloc[0] == 100.0 * gbp_rate


def test_calculate_investor_metrics() -> None:
    # Pick the first investor
    investor_id = loader.investors.iloc[0]["investor_id"]
    metrics = calculate_investor_metrics(investor_id)

    assert "moic" in metrics
    assert "dpi" in metrics
    assert "rvpi" in metrics
    assert "cost_basis" in metrics
    assert "current_value" in metrics

    # Validations
    assert metrics["cost_basis"] >= 0
    assert metrics["moic"] >= 0


def test_calculate_effective_fee() -> None:
    # Pick a deal and an investor
    if not loader.allocations.empty:
        alloc = loader.allocations.iloc[0]
        fees = calculate_effective_fee(alloc["deal_id"], alloc["investor_id"])

        assert "effective_mgmt_fee_pct" in fees
        assert "standard_mgmt_fee_pct" in fees
        assert "discount_applied" in fees
        assert isinstance(fees["discount_applied"], bool)


def test_build_personalisation_profile() -> None:
    # Pick the first investor
    investor_id = loader.investors.iloc[0]["investor_id"]
    profile = build_personalisation_profile(investor_id)

    assert "age" in profile
    assert "tech_savviness" in profile
    assert "deal_count" in profile
    assert "guidance" in profile
    assert isinstance(profile["top_sectors"], list)
    assert "Tone:" in profile["guidance"]
