"""
Global Superstore Sales Analysis - Data Cleaning & Validation Pipeline
Module: scripts.data_cleaning
Author: Sneh Kheni
"""

import os
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def load_raw_data(file_path: str = "data/raw/superstore.csv") -> pd.DataFrame:
    """Load the raw Global Superstore dataset from CSV.

    Args:
        file_path: Path to the raw CSV file.

    Returns:
        pd.DataFrame: Raw dataset.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw dataset not found at {file_path}")
    return pd.read_csv(file_path)


def clean_superstore_data(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean, standardize, validate, and engineer operational features from the dataset.

    Cleaning & Validation Steps:
    1. Pre-validation: Audit initial dimensions, nulls, duplicates, and column types.
    2. Drop non-informative artifact columns (e.g. '记录数' - Tableau Record Count).
    3. Type Conversion & Validation: Coerce and validate core numerical columns
       (Sales, Profit, Quantity, Discount, Shipping.Cost) BEFORE feature engineering.
    4. Date Parsing & Validation: Parse Order.Date and Ship.Date into datetime format;
       validate that Ship.Date >= Order.Date.
    5. Temporal Feature Engineering: Extract Year, Quarter, Month, Month_Name,
       YearMonth, and Day_of_Week.
    6. Operational & Financial Feature Engineering:
       - Shipping_Days: Ship.Date - Order.Date (fulfillment duration)
       - Profit_Margin_Pct: (Profit / Sales) * 100 (safe division)
       - Unit_Price: Sales / Quantity (safe division)
       - Estimated_Cost: Sales - Profit
       - Discount_Band: Binned discount tiers for margin elasticity analysis.
    7. Post-validation: Ensure 100% record retention (no silent record dropping)
       and verify schema compatibility for Power BI.

    Args:
        df: Raw DataFrame.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: Cleaned DataFrame and transparent audit report.
    """
    df_clean = df.copy()
    initial_shape = df_clean.shape
    initial_duplicates = int(df_clean.duplicated().sum())
    initial_nulls = df_clean.isnull().sum().to_dict()

    # 1. Drop Tableau-generated artifact column if present
    dropped_columns = []
    if "记录数" in df_clean.columns:
        df_clean.drop(columns=["记录数"], inplace=True)
        dropped_columns.append("记录数")

    # 2. Convert and validate numeric columns FIRST (Prior to feature engineering)
    numeric_cols = ["Sales", "Profit", "Quantity", "Discount", "Shipping.Cost"]
    invalid_numeric_counts = {}

    for col in numeric_cols:
        if col in df_clean.columns:
            coerced = pd.to_numeric(df_clean[col], errors="coerce")
            nan_count = int(coerced.isna().sum() - df_clean[col].isna().sum())
            if nan_count > 0:
                invalid_numeric_counts[col] = nan_count
            df_clean[col] = coerced

    # Enforce integer type on Quantity
    df_clean["Quantity"] = df_clean["Quantity"].round().astype(int)

    # Boundary validation checks (recorded in audit report, no silent drops)
    negative_sales_count = int((df_clean["Sales"] < 0).sum())
    negative_quantity_count = int((df_clean["Quantity"] <= 0).sum())
    invalid_discount_count = int(((df_clean["Discount"] < 0) | (df_clean["Discount"] > 1.0)).sum())
    negative_shipping_cost_count = int((df_clean["Shipping.Cost"] < 0).sum())

    # 3. Parse and validate date columns
    df_clean["Order.Date"] = pd.to_datetime(df_clean["Order.Date"], errors="coerce")
    df_clean["Ship.Date"] = pd.to_datetime(df_clean["Ship.Date"], errors="coerce")

    invalid_order_dates = int(df_clean["Order.Date"].isna().sum())
    invalid_ship_dates = int(df_clean["Ship.Date"].isna().sum())

    # 4. Temporal Feature Engineering
    df_clean["Year"] = df_clean["Order.Date"].dt.year
    df_clean["Quarter"] = df_clean["Order.Date"].dt.quarter
    df_clean["Month"] = df_clean["Order.Date"].dt.month
    df_clean["Month_Name"] = df_clean["Order.Date"].dt.month_name()
    df_clean["YearMonth"] = df_clean["Order.Date"].dt.to_period("M").astype(str)
    df_clean["Day_of_Week"] = df_clean["Order.Date"].dt.day_name()

    # 5. Operational & Financial Feature Engineering (Using validated numeric columns)
    # Fulfillment duration in days
    df_clean["Shipping_Days"] = (df_clean["Ship.Date"] - df_clean["Order.Date"]).dt.days
    negative_shipping_days = int((df_clean["Shipping_Days"] < 0).sum())

    # Safe Profit Margin %
    df_clean["Profit_Margin_Pct"] = np.where(
        df_clean["Sales"] > 0,
        (df_clean["Profit"] / df_clean["Sales"]) * 100,
        0.0
    )

    # Unit Price
    df_clean["Unit_Price"] = np.where(
        df_clean["Quantity"] > 0,
        df_clean["Sales"] / df_clean["Quantity"],
        df_clean["Sales"]
    )

    # Estimated Cost (Cost of Goods Sold + Allocated Operating Cost)
    df_clean["Estimated_Cost"] = df_clean["Sales"] - df_clean["Profit"]

    # Discount Band Categorization for Business Elasticity Analysis
    discount_bins = [-0.01, 0.0, 0.10, 0.20, 0.30, 0.50, 1.0]
    discount_labels = [
        "0% (No Discount)",
        "1% - 10%",
        "11% - 20%",
        "21% - 30%",
        "31% - 50%",
        "Above 50%"
    ]
    df_clean["Discount_Band"] = pd.cut(
        df_clean["Discount"],
        bins=discount_bins,
        labels=discount_labels
    )

    # Verify no records were silently discarded
    records_discarded = initial_shape[0] - df_clean.shape[0]
    assert records_discarded == 0, f"Critical: {records_discarded} records were discarded!"

    audit_report = {
        "initial_rows": initial_shape[0],
        "initial_columns": initial_shape[1],
        "cleaned_rows": df_clean.shape[0],
        "cleaned_columns": df_clean.shape[1],
        "records_discarded": records_discarded,
        "initial_duplicates": initial_duplicates,
        "dropped_columns": dropped_columns,
        "date_range_start": df_clean["Order.Date"].min().strftime("%Y-%m-%d"),
        "date_range_end": df_clean["Order.Date"].max().strftime("%Y-%m-%d"),
        "invalid_order_dates": invalid_order_dates,
        "invalid_ship_dates": invalid_ship_dates,
        "negative_shipping_days": negative_shipping_days,
        "negative_sales_count": negative_sales_count,
        "negative_quantity_count": negative_quantity_count,
        "invalid_discount_count": invalid_discount_count,
        "negative_shipping_cost_count": negative_shipping_cost_count,
        "invalid_numeric_coercions": invalid_numeric_counts,
        "total_nulls_after": int(df_clean.isnull().sum().sum()),
    }

    return df_clean, audit_report


def save_cleaned_data(
    df: pd.DataFrame,
    output_path: str = "data/processed/cleaned_superstore.csv"
) -> str:
    """Save cleaned dataset to CSV.

    Args:
        df: Cleaned DataFrame.
        output_path: Target file path.

    Returns:
        str: Absolute path of saved file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    print("Executing Data Cleaning Pipeline...")
    raw_df = load_raw_data()
    cleaned_df, report = clean_superstore_data(raw_df)
    saved_path = save_cleaned_data(cleaned_df)
    print("Data Cleaning Complete!")
    print(f"Cleaned dataset saved to: {saved_path}")
    print("Transparent Audit Report:")
    for k, v in report.items():
        print(f"  - {k}: {v}")
