from typing import Any, Dict

import pandas as pd

from .fx import convert_currency_vectorized
from .loader import data_store


def calculate_investor_metrics(investor_id: str) -> Dict[str, Any]:
    """
    Calculate MOIC, DPI, RVPI, current value, and cost basis.
    Strictly deterministic python math using vectorized operations.
    """
    allocations = data_store.allocations
    valuations = data_store.valuations
    distributions = data_store.distributions
    investors = data_store.investors

    if allocations.empty or investors.empty:
        return {}

    inv_row = investors[investors["investor_id"] == investor_id]
    if inv_row.empty:
        return {}
    reporting_currency = inv_row.iloc[0]["reporting_currency"]

    inv_allocs = allocations[allocations["investor_id"] == investor_id].copy()
    if inv_allocs.empty:
        return {
            "cost_basis": 0.0,
            "current_value": 0.0,
            "realized_value": 0.0,
            "moic": 0.0,
            "dpi": 0.0,
            "rvpi": 0.0,
            "reporting_currency": reporting_currency,
        }

    # 1. Cost Basis (Contributed Amount converted to reporting currency)
    reporting_currencies = pd.Series(
        [reporting_currency] * len(inv_allocs), index=inv_allocs.index
    )
    inv_allocs["cost_in_rep"] = convert_currency_vectorized(
        inv_allocs["contributed_amount"],
        inv_allocs["deal_currency"],
        reporting_currencies,
    )
    total_cost_basis = inv_allocs["cost_in_rep"].sum()

    # 2. Current Value
    # Get latest valuation per deal
    if not valuations.empty:
        latest_vals = (
            valuations.sort_values("valuation_date")
            .groupby("deal_id")
            .last()
            .reset_index()
        )
        allocs_with_vals = inv_allocs.merge(
            latest_vals[["deal_id", "share_price"]], on="deal_id", how="left"
        )
        allocs_with_vals["share_price"] = allocs_with_vals["share_price"].fillna(0)
        allocs_with_vals["current_value_deal"] = (
            allocs_with_vals["units"] * allocs_with_vals["share_price"]
        )

        rep_currs = pd.Series(
            [reporting_currency] * len(allocs_with_vals), index=allocs_with_vals.index
        )
        allocs_with_vals["current_val_rep"] = convert_currency_vectorized(
            allocs_with_vals["current_value_deal"],
            allocs_with_vals["deal_currency"],
            rep_currs,
        )
        total_current_value = allocs_with_vals["current_val_rep"].sum()
    else:
        total_current_value = 0.0

    # 3. Realized Value (Distributions)
    if not distributions.empty:
        inv_dists = distributions[distributions["investor_id"] == investor_id].copy()
        if not inv_dists.empty:
            rep_currs = pd.Series(
                [reporting_currency] * len(inv_dists), index=inv_dists.index
            )
            inv_dists["dist_rep"] = convert_currency_vectorized(
                inv_dists["net_amount"], inv_dists["currency"], rep_currs
            )
            total_realized = inv_dists["dist_rep"].sum()
        else:
            total_realized = 0.0
    else:
        total_realized = 0.0

    total_invested = total_cost_basis
    moic = 0.0
    dpi = 0.0
    rvpi = 0.0

    if total_invested > 0:
        moic = (total_realized + total_current_value) / total_invested
        dpi = total_realized / total_invested
        rvpi = total_current_value / total_invested

    return {
        "cost_basis": total_cost_basis,
        "current_value": total_current_value,
        "realized_value": total_realized,
        "moic": moic,
        "dpi": dpi,
        "rvpi": rvpi,
        "reporting_currency": reporting_currency,
    }
