"""
Global Superstore Sales Analysis - Time Series & Trend Analysis
Module: scripts.time_series
Author: Sneh Kheni
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def analyze_yearly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze yearly sales, profit, orders, and Year-over-Year (YoY) growth.

    CRITICAL FIX:
    Previous implementation sorted Year descending before calculating pct_change(),
    inverting YoY growth into negative numbers. This function enforces strict
    chronological ascending sorting (2011 -> 2012 -> 2013 -> 2014).

    Args:
        df: Cleaned Superstore DataFrame.

    Returns:
        pd.DataFrame: Yearly summary with YoY Sales and Profit growth percentages.
    """
    yearly = df.groupby("Year").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order.ID", "nunique"),
        Total_Quantity=("Quantity", "sum")
    ).sort_index(ascending=True)  # Enforce strict chronological order

    # Calculate YoY Growth (%)
    yearly["YoY_Sales_Growth_Pct"] = (yearly["Total_Sales"].pct_change() * 100).round(2)
    yearly["YoY_Profit_Growth_Pct"] = (yearly["Total_Profit"].pct_change() * 100).round(2)
    yearly["Profit_Margin_Pct"] = (yearly["Total_Profit"] / yearly["Total_Sales"] * 100).round(2)
    yearly["AOV"] = (yearly["Total_Sales"] / yearly["Total_Orders"]).round(2)

    return yearly.reset_index()


def calculate_cagr(start_val: float, end_val: float, periods: int) -> float:
    """Calculate Compound Annual Growth Rate (CAGR)."""
    if start_val <= 0 or periods <= 0:
        return 0.0
    return ((end_val / start_val) ** (1.0 / periods) - 1.0) * 100


def analyze_monthly_continuous_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze continuous monthly timeline across all 48 months (2011-01 to 2014-12)."""
    df_copy = df.copy()
    if "YearMonth" not in df_copy.columns:
        df_copy["YearMonth"] = pd.to_datetime(df_copy["Order.Date"]).dt.to_period("M").astype(str)

    monthly = df_copy.groupby("YearMonth").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order.ID", "nunique"),
        Total_Quantity=("Quantity", "sum"),
        Avg_Discount=("Discount", "mean")
    ).sort_index(ascending=True)

    monthly["Profit_Margin_Pct"] = (monthly["Total_Profit"] / monthly["Total_Sales"] * 100).round(2)
    monthly["MoM_Sales_Growth_Pct"] = (monthly["Total_Sales"].pct_change() * 100).round(2)
    monthly["Rolling_3M_Sales"] = monthly["Total_Sales"].rolling(window=3).mean().round(2)
    monthly["Rolling_3M_Profit"] = monthly["Total_Profit"].rolling(window=3).mean().round(2)

    return monthly.reset_index()


def analyze_quarterly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze quarterly trends across all years."""
    df_copy = df.copy()
    if "Quarter" not in df_copy.columns:
        df_copy["Quarter"] = pd.to_datetime(df_copy["Order.Date"]).dt.quarter
    if "Year" not in df_copy.columns:
        df_copy["Year"] = pd.to_datetime(df_copy["Order.Date"]).dt.year

    df_copy["Year_Quarter"] = df_copy["Year"].astype(str) + "-Q" + df_copy["Quarter"].astype(str)

    quarterly = df_copy.groupby(["Year", "Quarter", "Year_Quarter"]).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order.ID", "nunique")
    ).sort_index(ascending=True).reset_index()

    quarterly["Profit_Margin_Pct"] = (
        quarterly["Total_Profit"] / quarterly["Total_Sales"] * 100
    ).round(2)
    quarterly["QoQ_Sales_Growth_Pct"] = (quarterly["Total_Sales"].pct_change() * 100).round(2)
    return quarterly


def analyze_seasonality_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze historical month-of-year seasonal patterns (Jan through Dec)."""
    df_copy = df.copy()
    if "Month" not in df_copy.columns:
        df_copy["Month"] = pd.to_datetime(df_copy["Order.Date"]).dt.month

    seasonality = df_copy.groupby("Month").agg(
        Avg_Monthly_Sales=("Sales", "sum"),
        Avg_Monthly_Profit=("Profit", "sum"),
        Total_Orders=("Order.ID", "nunique")
    ).sort_index(ascending=True).reset_index()

    # 4 active years: 2011 to 2014
    seasonality["Avg_Sales_Per_Year"] = (seasonality["Avg_Monthly_Sales"] / 4.0).round(2)
    seasonality["Avg_Profit_Per_Year"] = (seasonality["Avg_Monthly_Profit"] / 4.0).round(2)

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    seasonality["Month_Name"] = seasonality["Month"].map(month_names)
    seasonality["Profit_Margin_Pct"] = (
        seasonality["Avg_Monthly_Profit"] / seasonality["Avg_Monthly_Sales"] * 100
    ).round(2)

    return seasonality


if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_superstore.csv")
    print("--- Yearly Performance (Chronological) ---")
    yearly = analyze_yearly_trends(df)
    print(yearly.to_string(index=False))

    cagr_sales = calculate_cagr(yearly.iloc[0]["Total_Sales"], yearly.iloc[-1]["Total_Sales"], 3)
    cagr_profit = calculate_cagr(yearly.iloc[0]["Total_Profit"], yearly.iloc[-1]["Total_Profit"], 3)
    print(f"\n3-Year Sales CAGR (2011-2014): {cagr_sales:.2f}%")
    print(f"3-Year Profit CAGR (2011-2014): {cagr_profit:.2f}%")
