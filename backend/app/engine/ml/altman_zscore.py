"""
Altman Z-Score model for vendor financial health prediction.
Phase 2: Connect to MCA21/financial data sources.

Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

Where:
  X1 = Working Capital / Total Assets
  X2 = Retained Earnings / Total Assets
  X3 = EBIT / Total Assets
  X4 = Market Value of Equity / Total Liabilities
  X5 = Sales / Total Assets

Zones:
  Z > 2.99  -> Safe zone      (score 75-100)
  1.81-2.99 -> Grey zone      (score 40-74)
  Z < 1.81  -> Distress zone  (score 0-39)
"""
from dataclasses import dataclass


@dataclass
class VendorFinancials:
    working_capital: float
    total_assets: float
    retained_earnings: float
    ebit: float
    market_value_equity: float
    total_liabilities: float
    sales: float


def calculate_altman_z(financials: VendorFinancials) -> tuple[float, int, str]:
    """
    Returns (z_score, risk_score_0_100, zone).
    """
    ta = financials.total_assets
    if ta == 0:
        return 0.0, 0, "distress"

    x1 = financials.working_capital / ta
    x2 = financials.retained_earnings / ta
    x3 = financials.ebit / ta
    x4 = (
        financials.market_value_equity / financials.total_liabilities
        if financials.total_liabilities > 0
        else 0
    )
    x5 = financials.sales / ta

    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

    if z > 2.99:
        zone = "safe"
        score = min(100, int(75 + (z - 2.99) * 8))
    elif z >= 1.81:
        zone = "grey"
        score = int(40 + (z - 1.81) / (2.99 - 1.81) * 34)
    else:
        zone = "distress"
        score = max(0, int(z / 1.81 * 39))

    return z, score, zone
