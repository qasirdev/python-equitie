from typing import Any, Dict, List

from ..data_layer.loader import data_store
from ..data_layer.metrics import calculate_investor_metrics


def get_portfolio_overview(investor_id: str) -> Dict[str, Any]:
    metrics = calculate_investor_metrics(investor_id)

    allocations = data_store.allocations
    deals = data_store.deals
    companies = data_store.portfolio_companies

    holdings = []
    total_committed = 0.0
    total_contributed = metrics.get("cost_basis", 0.0)

    if not allocations.empty and not deals.empty and not companies.empty:
        inv_allocs = allocations[allocations["investor_id"] == investor_id]
        total_committed = inv_allocs["commitment_amount"].sum()

        merged = inv_allocs.merge(deals, on="deal_id", how="left").merge(
            companies, on="company_id", how="left"
        )
        for _, row in merged.iterrows():
            holdings.append(
                {
                    "company_name": row.get("company_name", "Unknown"),
                    "deal_id": row.get("deal_id"),
                    "round": row.get("round"),
                    "units": row.get("units"),
                }
            )

    metrics["holdings"] = holdings
    metrics["total_committed"] = total_committed
    metrics["total_contributed"] = total_contributed
    return metrics


def get_single_position(investor_id: str, deal_id: str) -> Dict[str, Any]:
    allocations = data_store.allocations
    valuations = data_store.valuations
    deals = data_store.deals

    inv_allocs = allocations[
        (allocations["investor_id"] == investor_id)
        & (allocations["deal_id"] == deal_id)
    ]
    if inv_allocs.empty:
        return {"error": "Position not found for the given deal_id"}

    row = inv_allocs.iloc[0]

    current_value = 0.0
    share_price = 0.0
    if not valuations.empty:
        deal_vals = valuations[valuations["deal_id"] == deal_id].sort_values(
            "valuation_date"
        )
        if not deal_vals.empty:
            share_price = deal_vals.iloc[-1]["share_price"]
            current_value = row["units"] * share_price

    # Include deal info (e.g. entry share price)
    deal_info = deals[deals["deal_id"] == deal_id]
    entry_share_price = (
        deal_info.iloc[0]["entry_share_price"] if not deal_info.empty else None
    )

    return {
        "deal_id": deal_id,
        "units": row["units"],
        "cost_basis": row["contributed_amount"],
        "deal_currency": row["deal_currency"],
        "current_value": current_value,
        "latest_share_price": share_price,
        "entry_share_price": entry_share_price,
        "discount_pct": row["price_discount_pct"],
    }


def get_obligations(investor_id: str) -> Dict[str, Any]:
    fees = data_store.fees
    calls = data_store.capital_calls

    inv_fees = (
        fees[(fees["investor_id"] == investor_id) & (fees["status"] == "overdue")]
        if not fees.empty
        else []
    )
    inv_calls = (
        calls[(calls["investor_id"] == investor_id) & (calls["status"] == "upcoming")]
        if not calls.empty
        else []
    )

    return {
        "overdue_fees": inv_fees.to_dict(orient="records")
        if not isinstance(inv_fees, list)
        else [],
        "upcoming_calls": inv_calls.to_dict(orient="records")
        if not isinstance(inv_calls, list)
        else [],
    }


def get_realised_outcomes(investor_id: str) -> List[Dict[str, Any]]:
    distributions = data_store.distributions
    if distributions.empty:
        return []
    inv_dists = distributions[distributions["investor_id"] == investor_id]
    return inv_dists.to_dict(orient="records")


def get_fees_schedule(investor_id: str, deal_id: str) -> Dict[str, Any]:
    allocations = data_store.allocations
    inv_allocs = allocations[
        (allocations["investor_id"] == investor_id)
        & (allocations["deal_id"] == deal_id)
    ]
    if inv_allocs.empty:
        return {"error": "No allocation found"}
    row = inv_allocs.iloc[0]
    return {
        "mgmt_fee_pct": row.get("mgmt_fee_pct"),
        "performance_fee_pct": row.get("performance_fee_pct"),
        "fee_discount": row.get("fee_discount"),
    }


def get_valuation_history(deal_id: str) -> List[Dict[str, Any]]:
    valuations = data_store.valuations
    if valuations.empty:
        return []
    deal_vals = valuations[valuations["deal_id"] == deal_id].sort_values(
        "valuation_date"
    )
    return deal_vals.to_dict(orient="records")


def get_account_statement(investor_id: str) -> List[Dict[str, Any]]:
    statements = data_store.statement_lines
    if statements.empty:
        return []
    inv_stmt = statements[statements["investor_id"] == investor_id].sort_values("date")
    return inv_stmt.to_dict(orient="records")


def resolve_entity(query: str, entity_type: str = "company") -> Dict[str, Any]:
    """Fuzzy match companies or deals."""
    if entity_type == "company" and not data_store.portfolio_companies.empty:
        comps = data_store.portfolio_companies
        matches = comps[comps["company_name"].str.contains(query, case=False, na=False)]
        return matches.to_dict(orient="records")
    return {"error": "No matching entity found"}


TOOLS_REGISTRY = {
    "get_portfolio_overview": get_portfolio_overview,
    "get_single_position": get_single_position,
    "get_obligations": get_obligations,
    "get_realised_outcomes": get_realised_outcomes,
    "get_fees_schedule": get_fees_schedule,
    "get_valuation_history": get_valuation_history,
    "get_account_statement": get_account_statement,
    "resolve_entity": resolve_entity,
}

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_portfolio_overview",
            "description": "Get portfolio overview (holdings, current value, MOIC, committed vs contributed) for an investor.",
            "parameters": {
                "type": "object",
                "properties": {"investor_id": {"type": "string"}},
                "required": ["investor_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_single_position",
            "description": "Get single position details (current value, cost basis, share price paid across rounds) for a specific deal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "investor_id": {"type": "string"},
                    "deal_id": {"type": "string"},
                },
                "required": ["investor_id", "deal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_obligations",
            "description": "Get upcoming capital calls and overdue management fees for an investor.",
            "parameters": {
                "type": "object",
                "properties": {"investor_id": {"type": "string"}},
                "required": ["investor_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_realised_outcomes",
            "description": "Get realised outcomes (distributions, exits, net of carry/performance fee) for an investor.",
            "parameters": {
                "type": "object",
                "properties": {"investor_id": {"type": "string"}},
                "required": ["investor_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fees_schedule",
            "description": "Get fees schedule (deal standard schedule vs investor discount) for a specific deal allocation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "investor_id": {"type": "string"},
                    "deal_id": {"type": "string"},
                },
                "required": ["investor_id", "deal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_valuation_history",
            "description": "Get valuation history affecting investor MOIC for a specific deal.",
            "parameters": {
                "type": "object",
                "properties": {"deal_id": {"type": "string"}},
                "required": ["deal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_account_statement",
            "description": "Get plain language summary of capital contributions, fees, and distributions for an investor.",
            "parameters": {
                "type": "object",
                "properties": {"investor_id": {"type": "string"}},
                "required": ["investor_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "resolve_entity",
            "description": "Resolve similar company names via fuzzy match to get exact IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The name of the company or entity to search for.",
                    },
                    "entity_type": {"type": "string", "enum": ["company", "deal"]},
                },
                "required": ["query"],
            },
        },
    },
]
