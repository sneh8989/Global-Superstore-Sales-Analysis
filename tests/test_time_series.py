"""
Unit Tests - Time Series Analysis and Chronological Sorting
"""

import pytest
import pandas as pd
from scripts.time_series import (
    analyze_yearly_trends,
    analyze_monthly_continuous_trends,
    analyze_quarterly_trends,
    calculate_cagr,
)


@pytest.fixture(scope="module")
def df_cleaned():
    return pd.read_csv("data/processed/cleaned_superstore.csv")


def test_chronological_yearly_sorting(df_cleaned):
    """Yearly analysis must be strictly chronological (2011 to 2014)."""
    yearly = analyze_yearly_trends(df_cleaned)
    years = yearly["Year"].tolist()
    assert years == [2011, 2012, 2013, 2014]


def test_positive_yoy_sales_growth(df_cleaned):
    """
    REGRESSION TEST FOR CRITICAL TIME-SERIES BUG:
    Sales grew year-over-year throughout 2011-2014. Growth rates must be positive!
    Previous bug inverted growth to negative due to descending year sort.
    """
    yearly = analyze_yearly_trends(df_cleaned)
    growth_rates = yearly["YoY_Sales_Growth_Pct"].dropna().tolist()

    # 2012 vs 2011: ~18.50%
    # 2013 vs 2012: ~27.20%
    # 2014 vs 2013: ~26.25%
    for rate in growth_rates:
        assert rate > 0, f"YoY sales growth should be positive, got {rate}%"

    assert growth_rates[0] == pytest.approx(18.50, abs=0.1)
    assert growth_rates[1] == pytest.approx(27.20, abs=0.1)
    assert growth_rates[2] == pytest.approx(26.25, abs=0.1)


def test_positive_yoy_profit_growth(df_cleaned):
    """Profit grew year-over-year throughout 2011-2014."""
    yearly = analyze_yearly_trends(df_cleaned)
    profit_growth = yearly["YoY_Profit_Growth_Pct"].dropna().tolist()

    for rate in profit_growth:
        assert rate > 0, f"YoY profit growth should be positive, got {rate}%"

    assert profit_growth[0] == pytest.approx(23.49, abs=0.1)
    assert profit_growth[1] == pytest.approx(32.37, abs=0.1)
    assert profit_growth[2] == pytest.approx(23.89, abs=0.1)


def test_monthly_continuous_48_months(df_cleaned):
    """Monthly continuous trend must contain exactly 48 months (2011-01 to 2014-12)."""
    monthly = analyze_monthly_continuous_trends(df_cleaned)
    assert len(monthly) == 48
    assert monthly.iloc[0]["YearMonth"] == "2011-01"
    assert monthly.iloc[-1]["YearMonth"] == "2014-12"


def test_cagr_calculation():
    """Verify CAGR formula correctness."""
    cagr = calculate_cagr(100.0, 200.0, 3)
    # (200/100)^(1/3) - 1 = 2^(1/3) - 1 = 1.25992 - 1 = 25.99%
    assert cagr == pytest.approx(25.992, abs=0.01)
