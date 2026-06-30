import pandas as pd

from .loader import data_store


from typing import Dict, Any


def calculate_effective_fee(deal_id: str, investor_id: str) -> Dict[str, Any]:
    """
    Calculate effective rate vs deal standard schedule.
    Applies per-investor fee_discount flag.
    """
    allocations = data_store.allocations
    deals = data_store.deals

    if allocations.empty or deals.empty:
        return {}

    alloc_row = allocations[
        (allocations["deal_id"] == deal_id)
        & (allocations["investor_id"] == investor_id)
    ]
    deal_row = deals[deals["deal_id"] == deal_id]

    if alloc_row.empty or deal_row.empty:
        return {}

    alloc = alloc_row.iloc[0]
    deal = deal_row.iloc[0]

    std_mgmt = deal["std_mgmt_fee_pct"]
    std_perf = deal["std_performance_fee_pct"]

    eff_mgmt = alloc["mgmt_fee_pct"]
    eff_perf = alloc["performance_fee_pct"]

    discount_applied = alloc["fee_discount"] == "Yes"

    return {
        "standard_mgmt_fee_pct": float(std_mgmt) if pd.notna(std_mgmt) else 0.0,
        "standard_performance_fee_pct": float(std_perf) if pd.notna(std_perf) else 0.0,
        "effective_mgmt_fee_pct": float(eff_mgmt) if pd.notna(eff_mgmt) else 0.0,
        "effective_performance_fee_pct": float(eff_perf) if pd.notna(eff_perf) else 0.0,
        "discount_applied": discount_applied,
    }
