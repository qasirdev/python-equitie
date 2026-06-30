import pandas as pd

from .loader import data_store


def get_fx_rate_series(currencies: pd.Series) -> pd.Series:
    """Returns a series of to_usd rates matching the input currencies series."""
    fx_df = data_store.fx_rates
    if fx_df.empty:
        return pd.Series(1.0, index=currencies.index)

    rates_map = dict(zip(fx_df["currency"], fx_df["to_usd"]))
    # USD defaults to 1.0, missing defaults to 1.0
    rates_map["USD"] = 1.0

    return currencies.map(rates_map).fillna(1.0)


def convert_currency_vectorized(
    amounts: pd.Series, from_currencies: pd.Series, to_currencies: pd.Series
) -> pd.Series:
    """
    Converts a Series of amounts from one currency to another using vectorized ops.
    """
    from_usd_rates = get_fx_rate_series(from_currencies)
    to_usd_rates = get_fx_rate_series(to_currencies)

    # Avoid division by zero
    to_usd_rates = to_usd_rates.replace(0.0, 1.0)

    amount_in_usd = amounts * from_usd_rates
    return amount_in_usd / to_usd_rates


def process_statement_lines_fx() -> pd.DataFrame:
    """
    Returns a copy of statement lines with an additional 'converted_amount'
    and 'reporting_currency' column using entirely vectorized operations.
    """
    sl_df = data_store.statement_lines.copy()
    inv_df = data_store.investors

    if sl_df.empty or inv_df.empty:
        sl_df["converted_amount"] = pd.Series(dtype=float)
        return sl_df

    merged = sl_df.merge(
        inv_df[["investor_id", "reporting_currency"]], on="investor_id", how="left"
    )

    if not merged.empty:
        merged["converted_amount"] = convert_currency_vectorized(
            merged["amount"], merged["currency"], merged["reporting_currency"]
        )
    else:
        merged["converted_amount"] = pd.Series(dtype=float)

    return merged
