"""
Unit Tests - Enterprise KPI Engine & Parity Verification
"""

import pytest
import pandas as pd
from scripts.kpi_engine import (
    compute_executive_kpis,
    compute_category_kpis,
    compute_segment_kpis,
    compute_market_kpis,
)


@pytest.fixture(scope="module")
def df_cleaned():
    return pd.read_csv("data/processed/cleaned_superstore.csv")


def test_executive_kpi_values(df_cleaned):
    """Executive KPIs must match verified ground truth and DAX calculations."""
    kpis = compute_executive_kpis(df_cleaned)
    
    # Ground truth values:
    # Sales: 12,642,905.00
    # Profit: 1,467,457.29
    # Margin: 11.61%
    # Orders: 25,035
    # Customers: 4,873
    # Quantity: 178,312
    # AOV: 505.01
    assert kpis["total_sales"] == pytest.approx(12642905.00, rel=1e-3)
    assert kpis["total_profit"] == pytest.approx(1467457.29, rel=1e-3)
    assert kpis["profit_margin_pct"] == pytest.approx(11.61, abs=0.05)
    assert kpis["total_orders"] == 25035
    assert kpis["total_customers"] == 4873
    assert kpis["total_quantity"] == 178312
    assert kpis["avg_order_value"] == pytest.approx(505.01, abs=0.05)
    assert kpis["avg_profit_per_order"] == pytest.approx(58.62, abs=0.05)


def test_category_reconciliation(df_cleaned):
    """Sum of category sales and profit must equal total sales and profit."""
    kpis = compute_executive_kpis(df_cleaned)
    cat_df = compute_category_kpis(df_cleaned)
    
    assert cat_df["Total_Sales"].sum() == pytest.approx(kpis["total_sales"], rel=1e-4)
    assert cat_df["Total_Profit"].sum() == pytest.approx(kpis["total_profit"], rel=1e-4)
    assert cat_df["Sales_Share_Pct"].sum() == pytest.approx(100.0, abs=0.1)


def test_segment_reconciliation(df_cleaned):
    """Sum of segment sales must equal total sales."""
    kpis = compute_executive_kpis(df_cleaned)
    seg_df = compute_segment_kpis(df_cleaned)
    
    assert seg_df["Total_Sales"].sum() == pytest.approx(kpis["total_sales"], rel=1e-4)
    assert seg_df["Total_Profit"].sum() == pytest.approx(kpis["total_profit"], rel=1e-4)
