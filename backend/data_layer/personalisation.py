from .loader import data_store


from typing import Dict, Any

def build_personalisation_profile(investor_id: str) -> Dict[str, Any]:
    """
    Build PersonalisationProfile context from age, tech_savviness,
    AND derived signals (how many deals they are in, most-invested sectors).
    """
    investors = data_store.investors
    allocations = data_store.allocations
    deals = data_store.deals
    companies = data_store.portfolio_companies

    if investors.empty:
        return {}

    inv_row = investors[investors["investor_id"] == investor_id]
    if inv_row.empty:
        return {}

    inv = inv_row.iloc[0]

    profile: Dict[str, Any] = {
        "age": int(inv["age"]),
        "tech_savviness": str(inv["tech_savviness"]),
        "deal_count": 0,
        "top_sectors": [],
        "guidance": ""
    }

    # Calculate derived signals
    if not allocations.empty and not deals.empty and not companies.empty:
        inv_allocs = allocations[allocations["investor_id"] == investor_id]
        profile["deal_count"] = len(inv_allocs)

        # Get sectors
        merged = inv_allocs.merge(deals, on="deal_id").merge(companies, on="company_id")
        if not merged.empty:
            sector_counts = merged["sector"].value_counts()
            profile["top_sectors"] = sector_counts.head(2).index.tolist()

    # Tone guidance based on age and tech savviness
    is_older = int(profile["age"]) > 60
    is_tech_savvy = str(profile["tech_savviness"]).lower() == "high"

    if is_tech_savvy:
        tone = "Concise and data-dense. Use industry standard terminology like MOIC, DPI, Carry, and TVPI without over-explaining."
    elif is_older:
        tone = "Respectful, clear, and plain language. Avoid jargon. Explain terms like 'MOIC' (Multiple on Invested Capital) or 'Carry' (Performance Fee) in simple terms if used."
    else:
        tone = "Professional and balanced. Clear language, avoiding overly complex financial jargon without being patronising."

    guidance = f"Tone: {tone} Contextualize answers by acknowledging their {profile['deal_count']} investments"
    if profile["top_sectors"]:
        sectors_str = ', '.join(str(s) for s in profile["top_sectors"])
        guidance += f", heavily weighted towards {sectors_str}."
    else:
        guidance += "."

    profile["guidance"] = guidance

    return profile
