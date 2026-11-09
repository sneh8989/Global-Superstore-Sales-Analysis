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
    """Clean, standardize, and engineer operational features from the dataset.
    
    Cleaning steps:
    1. Validate dimensions, null values, and duplicate rows.
    2. Remove non-informative / artifact columns (e.g., '记录数').
    3. Parse date columns into datetime format.
    4. Engineer temporal attributes (Year, Quarter, Month, Month_Name, YearMonth, Day_of_Week).
    5. Engineer operational & financial metrics:
       - Shipping_Days: Ship.Date - Order.Date (fulfillment duration)
       - Profit_Margin_Pct: (Profit / Sales) * 100
       - Unit_Price: Sales / Quantity
       - Estimated_Cost: Sales - Profit
    6. Ensure strict type consistency.
    
    Args:
        df: Raw DataFrame.
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: Cleaned DataFrame and audit report dictionary.
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
        
    # 2. Date Parsing
    df_clean["Order.Date"] = pd.to_datetime(df_clean["Order.Date"], errors="coerce")
    df_clean["Ship.Date"] = pd.to_datetime(df_clean["Ship.Date"], errors="coerce")
    
    # 3. Temporal Feature Engineering
    df_clean["Year"] = df_clean["Order.Date"].dt.year
    df_clean["Quarter"] = df_clean["Order.Date"].dt.quarter
    df_clean["Month"] = df_clean["Order.Date"].dt.month
    df_clean["Month_Name"] = df_clean["Order.Date"].dt.month_name()
    df_clean["YearMonth"] = df_clean["Order.Date"].dt.to_period("M").astype(str)
    df_clean["Day_of_Week"] = df_clean["Order.Date"].dt.day_name()
    
    # 4. Operational & Financial Feature Engineering
    # Fulfillment duration in days
    df_clean["Shipping_Days"] = (df_clean["Ship.Date"] - df_clean["Order.Date"]).dt.days
    
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
    
    # Estimated Cost of Goods Sold + Allocated Operating Cost
    df_clean["Estimated_Cost"] = df_clean["Sales"] - df_clean["Profit"]
    
    # 5. Type Enforcement
    df_clean["Sales"] = pd.to_numeric(df_clean["Sales"], errors="coerce")
    df_clean["Profit"] = pd.to_numeric(df_clean["Profit"], errors="coerce")
    df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"], errors="coerce").astype(int)
    df_clean["Discount"] = pd.to_numeric(df_clean["Discount"], errors="coerce")
    df_clean["Shipping.Cost"] = pd.to_numeric(df_clean["Shipping.Cost"], errors="coerce")
    
    # 6. Discount Band Categorization for Business Analysis
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
    
    audit_report = {
        "initial_rows": initial_shape[0],
        "initial_columns": initial_shape[1],
        "cleaned_rows": df_clean.shape[0],
        "cleaned_columns": df_clean.shape[1],
        "initial_duplicates": initial_duplicates,
        "dropped_columns": dropped_columns,
        "date_range_start": df_clean["Order.Date"].min().strftime("%Y-%m-%d"),
        "date_range_end": df_clean["Order.Date"].max().strftime("%Y-%m-%d"),
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
    print(f"Summary: {report}")

