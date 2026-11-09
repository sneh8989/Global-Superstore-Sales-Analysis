"""
Unit Tests - Power BI Dashboard & Output Artifacts Integrity
"""

import os
import zipfile
import pytest
import pandas as pd


def test_pbix_file_exists_and_valid():
    """SuperstoreDashboard.pbix must exist and be a valid Power BI archive."""
    pbix_path = "dashboard/SuperstoreDashboard.pbix"
    assert os.path.exists(pbix_path), f"PBIX file not found at {pbix_path}"
    assert os.path.getsize(pbix_path) > 1_000_000, "PBIX file is unexpectedly small"
    
    with zipfile.ZipFile(pbix_path, "r") as z:
        names = z.namelist()
        assert "Report/Layout" in names, "Missing Report/Layout in PBIX"
        assert "DataModel" in names, "Missing DataModel in PBIX"


def test_power_bi_column_dependencies():
    """Verify that cleaned_superstore.csv maintains all columns required by Power BI visuals."""
    df_cleaned = pd.read_csv("data/processed/cleaned_superstore.csv")
    
    # Exact columns referenced in Power BI Report/Layout
    pbi_required_columns = [
        "Category",
        "Sub.Category",
        "Year",
        "Segment",
        "Region",
        "Discount",
        "Ship.Mode",
        "Order.Priority",
        "Customer.Name",
        "Product.Name",
        "Country",
        "Market",
        "Sales",
        "Profit",
        "Quantity",
        "Order.ID",
        "Order.Date"
    ]
    for col in pbi_required_columns:
        assert col in df_cleaned.columns, f"Power BI dependency missing in CSV: {col}"


def test_visual_outputs_exist():
    """Ensure all core high-resolution visual outputs exist and are non-empty."""
    expected_visuals = [
        "01_monthly_sales_profit_trend.png",
        "02_sales_profit_by_category.png",
        "03_sub_category_profitability.png",
        "04_regional_performance.png",
        "05_discount_vs_profit_elasticity.png",
        "06_top_bottom_products.png",
        "07_customer_segment_distribution.png",
        "discount_profit_trend.png",
    ]
    for vis in expected_visuals:
        p = os.path.join("outputs/visuals", vis)
        assert os.path.exists(p), f"Visual missing: {p}"
        assert os.path.getsize(p) > 20_000, f"Visual unexpectedly small or corrupt: {p}"


def test_excel_reports_exist():
    """Ensure generated Excel reports exist and are non-empty."""
    master_report = "outputs/reports/global_superstore_executive_report.xlsx"
    assert os.path.exists(master_report), f"Master report missing: {master_report}"
    assert os.path.getsize(master_report) > 5000, "Master report file size too small"
    
    pivot_table = "outputs/pivot_tables/sales_by_category_segment.xlsx"
    assert os.path.exists(pivot_table), f"Pivot table missing: {pivot_table}"
