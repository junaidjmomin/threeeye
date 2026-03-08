"""Tests for Altman Z-Score financial health model."""
from app.engine.ml.altman_zscore import VendorFinancials, calculate_altman_z


def test_safe_zone():
    financials = VendorFinancials(
        working_capital=500,
        total_assets=1000,
        retained_earnings=300,
        ebit=200,
        market_value_equity=800,
        total_liabilities=400,
        sales=900,
    )
    z, score, zone = calculate_altman_z(financials)
    assert z > 2.99
    assert zone == "safe"
    assert score >= 75


def test_grey_zone():
    financials = VendorFinancials(
        working_capital=100,
        total_assets=1000,
        retained_earnings=50,
        ebit=60,
        market_value_equity=400,
        total_liabilities=600,
        sales=500,
    )
    z, score, zone = calculate_altman_z(financials)
    assert 1.81 <= z <= 2.99
    assert zone == "grey"
    assert 40 <= score <= 74


def test_distress_zone():
    financials = VendorFinancials(
        working_capital=-100,
        total_assets=1000,
        retained_earnings=-200,
        ebit=-50,
        market_value_equity=100,
        total_liabilities=900,
        sales=200,
    )
    z, score, zone = calculate_altman_z(financials)
    assert z < 1.81
    assert zone == "distress"
    assert score < 40


def test_zero_assets():
    financials = VendorFinancials(
        working_capital=0,
        total_assets=0,
        retained_earnings=0,
        ebit=0,
        market_value_equity=0,
        total_liabilities=0,
        sales=0,
    )
    z, score, zone = calculate_altman_z(financials)
    assert z == 0.0
    assert zone == "distress"
