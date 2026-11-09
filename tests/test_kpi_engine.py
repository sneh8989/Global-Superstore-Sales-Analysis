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


def test_row_counts_vs_distinct_order_counts(df_cleaned):
    """
    Test and verify the explicit distinction between total line items
    (row count) and distinct customer orders.
    """
    kpis = compute_executive_kpis(df_cleaned)
    assert kpis["total_line_items"] == 51290, "Total line items (rows) must equal 51,290"
    assert kpis["total_orders"] == 25035, "Unique order count must equal 25,035"
    assert kpis["total_line_items"] > kpis["total_orders"], "Row count must exceed distinct order count"

    # Average line items per unique order
    items_per_order = kpis["total_line_items"] / kpis["total_orders"]
    assert items_per_order == pytest.approx(2.0487, abs=0.01)


def test_loss_line_items_vs_loss_orders(df_cleaned):
    """
    Verify the distinction between loss-making line items, unique orders
    containing at least one loss, and orders with net negative total profit.
    """
    kpis = compute_executive_kpis(df_cleaned)
    assert kpis["loss_making_line_items"] == 12544, "Loss-making line items must equal 12,544"
    assert kpis["loss_making_line_items_pct"] == pytest.approx(24.46, abs=0.01)

    assert kpis["orders_with_losses"] == 7541, "Orders containing >= 1 loss line item must equal 7,541"
    assert kpis["orders_with_losses_pct"] == pytest.approx(30.12, abs=0.01)

    assert kpis["net_loss_orders"] == 6125, "Orders with net negative cumulative profit must equal 6,125"
    assert kpis["net_loss_orders_pct"] == pytest.approx(24.47, abs=0.01)

    assert kpis["loss_making_line_items"] > kpis["orders_with_losses"], (
        "Loss line items must exceed orders with losses because some orders contain multiple loss items"
    )
