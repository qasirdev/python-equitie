from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseStrictModel(BaseModel):
    model_config = ConfigDict(strict=True, coerce_numbers_to_str=False)


class Allocation(BaseStrictModel):
    allocation_id: str
    deal_id: str
    investor_id: str
    deal_currency: str
    commitment_amount: float
    price_discount_pct: float
    effective_share_price: float
    units: float
    contributed_amount: float
    outstanding_commitment: float
    mgmt_fee_pct: float
    performance_fee_pct: float
    structuring_fee_pct: float
    admin_fee_usd: float
    fee_discount: str
    allocation_status: str
    allocation_date: date


class CapitalCall(BaseStrictModel):
    call_id: str
    allocation_id: str
    investor_id: str
    deal_id: str
    call_number: int
    call_date: date
    amount: float
    currency: str
    due_date: date
    status: str


class Deal(BaseStrictModel):
    deal_id: str
    company_id: str
    company_name: str
    round: str
    instrument: str
    spv_name: str
    deal_currency: str
    deal_date: date
    pre_money_valuation_m: float
    post_money_valuation_m: float
    round_size_m: float
    equitie_allocation_m: float
    entry_share_price: float
    contributed_pct: float
    std_mgmt_fee_pct: float
    std_performance_fee_pct: float
    std_structuring_fee_pct: float
    std_admin_fee_usd: float
    status: str


class Distribution(BaseStrictModel):
    distribution_id: str
    deal_id: str
    allocation_id: str
    investor_id: str
    distribution_date: date
    distribution_type: str
    gross_amount: float
    performance_fee_pct: float
    performance_fee_amount: float
    net_amount: float
    currency: str
    fraction_of_units: float


class Fee(BaseStrictModel):
    fee_id: str
    allocation_id: str
    investor_id: str
    deal_id: str
    fee_type: str
    period: str
    fee_rate_pct: float
    basis: str
    amount: float
    currency: str
    due_date: date
    status: str


class FxRate(BaseStrictModel):
    currency: str
    to_usd: float
    as_of: date


class Investor(BaseStrictModel):
    investor_id: str
    investor_name: str
    investor_type: str
    country: str
    reporting_currency: str
    age: int
    tech_savviness: str
    kyc_status: str
    onboarded_date: date
    email: str


class PortfolioCompany(BaseStrictModel):
    company_id: str
    company_name: str
    sector: str
    hq_country: str
    status: str
    website: str


class StatementLine(BaseStrictModel):
    line_id: str
    investor_id: str
    date: date
    type: str
    deal_id: Optional[str] = None
    amount: float
    currency: str
    reference_id: Optional[str] = None


class Valuation(BaseStrictModel):
    valuation_id: str
    deal_id: str
    valuation_date: date
    share_price: float
    company_valuation_m: float
    mark_source: str
    multiple_vs_entry: float
