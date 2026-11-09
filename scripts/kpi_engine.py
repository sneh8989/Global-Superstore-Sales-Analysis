"""
Global Superstore Sales Analysis - Enterprise KPI Engine
Module: scripts.kpi_engine
Author: Sneh Kheni
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


def compute_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute top-level executive KPIs matching DAX and Python definitions.

    Terminology Specifications:
    - Line Items (Records): Individual transaction rows in the dataset (51,290 total).
    - Unique Orders: Distinct customer order identifiers Order.ID (25,035 total).
    - Loss-Making Line Items: Individual line items with negative Profit (< $0).
    - Orders Containing Losses: Unique Order.IDs containing >= 1 loss-making line item.
    - Net Loss Orders: Unique Order.IDs where aggregate net profit across all lines is < $0.

    Formula Reference:
    - Total Sales: sum(Sales)
    - Total Profit: sum(Profit)
    - Profit Margin %: (Total Profit / Total Sales) * 100
    - Total Orders: nunique(Order.ID)
    - Total Customers: nunique(Customer.ID)
    - Total Quantity: sum(Quantity)
    - Average Order Value (AOV): Total Sales / Total Orders
    - Average Profit per Order: Total Profit / Total Orders
    - Average Shipping Cost: mean(Shipping.Cost)
    - Average Delivery Days: mean(Shipping_Days)

    Args:
        df: Cleaned Superstore DataFrame.

    Returns:
        Dict[str, Any]: Key-value pair of all executive KPIs.
    """
    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())
    total_line_items = int(len(df))
    unique_orders = int(df["Order.ID"].nunique())
    customer_count = int(df["Customer.ID"].nunique())
    total_quantity = int(df["Quantity"].sum())

    profit_margin_pct = (total_profit / total_sales * 100) if total_sales else 0.0
    aov = (total_sales / unique_orders) if unique_orders else 0.0
    avg_profit_per_order = (total_profit / unique_orders) if unique_orders else 0.0
    avg_shipping_cost = float(df["Shipping.Cost"].mean())

    shipping_days_col = "Shipping_Days"
    if shipping_days_col not in df.columns and "Order.Date" in df.columns and "Ship.Date" in df.columns:
        shipping_days = (pd.to_datetime(df["Ship.Date"]) - pd.to_datetime(df["Order.Date"])).dt.days
        avg_shipping_days = float(shipping_days.mean())
    else:
        avg_shipping_days = float(df[shipping_days_col].mean()) if shipping_days_col in df.columns else 0.0

    # Precise Loss Item vs. Loss Order Metrics
    loss_making_line_items = int((df["Profit"] < 0).sum())
    loss_making_line_items_pct = (loss_making_line_items / total_line_items * 100) if total_line_items else 0.0

    orders_with_losses = int(df.loc[df["Profit"] < 0, "Order.ID"].nunique())
    orders_with_losses_pct = (orders_with_losses / unique_orders * 100) if unique_orders else 0.0

    order_profit_agg = df.groupby("Order.ID")["Profit"].sum()
    net_loss_orders = int((order_profit_agg < 0).sum())
    net_loss_orders_pct = (net_loss_orders / unique_orders * 100) if unique_orders else 0.0

    total_loss_amount = float(df.loc[df["Profit"] < 0, "Profit"].sum())

    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin_pct": round(profit_margin_pct, 2),
        "total_line_items": total_line_items,
        "total_orders": unique_orders,
        "total_customers": customer_count,
        "total_quantity": total_quantity,
        "avg_order_value": round(aov, 2),
        "avg_profit_per_order": round(avg_profit_per_order, 2),
        "avg_shipping_cost": round(avg_shipping_cost, 2),
        "avg_shipping_days": round(avg_shipping_days, 2),
        "loss_making_line_items": loss_making_line_items,
        "loss_making_line_items_pct": round(loss_making_line_items_pct, 2),
        "orders_with_losses": orders_with_losses,
        "orders_with_losses_pct": round(orders_with_losses_pct, 2),
        "net_loss_orders": net_loss_orders,
        "net_loss_orders_pct": round(net_loss_orders_pct, 2),
        "total_loss_amount": round(total_loss_amount, 2),
    }


def compute_category_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute KPI performance by Category distinguishing Line Items from Unique Orders."""
    cat_summary = df.groupby("Category").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Quantity=("Quantity", "sum"),
        Line_Item_Count=("Order.ID", "count"),
        Unique_Order_Count=("Order.ID", "nunique"),
        Avg_Discount=("Discount", "mean"),
    ).reset_index()

    cat_summary["Profit_Margin_Pct"] = (
        cat_summary["Total_Profit"] / cat_summary["Total_Sales"] * 100
    ).round(2)
    cat_summary["Sales_Share_Pct"] = (
        cat_summary["Total_Sales"] / cat_summary["Total_Sales"].sum() * 100
    ).round(2)
    cat_summary["Profit_Share_Pct"] = (
        cat_summary["Total_Profit"] / cat_summary["Total_Profit"].sum() * 100
    ).round(2)
    return cat_summary.sort_values(by="Total_Sales", ascending=False)


def compute_segment_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute KPI performance by Customer Segment."""
    seg_summary = df.groupby("Segment").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Quantity=("Quantity", "sum"),
        Line_Item_Count=("Order.ID", "count"),
        Unique_Order_Count=("Order.ID", "nunique"),
        Customer_Count=("Customer.ID", "nunique"),
    ).reset_index()

    seg_summary["Profit_Margin_Pct"] = (
        seg_summary["Total_Profit"] / seg_summary["Total_Sales"] * 100
    ).round(2)
    seg_summary["Sales_Share_Pct"] = (
        seg_summary["Total_Sales"] / seg_summary["Total_Sales"].sum() * 100
    ).round(2)
    seg_summary["Avg_Order_Value"] = (
        seg_summary["Total_Sales"] / seg_summary["Unique_Order_Count"]
    ).round(2)
    return seg_summary.sort_values(by="Total_Sales", ascending=False)


def compute_market_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute KPI performance by Market."""
    market_summary = df.groupby("Market").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Line_Item_Count=("Order.ID", "count"),
        Unique_Order_Count=("Order.ID", "nunique"),
        Avg_Shipping_Cost=("Shipping.Cost", "mean")
    ).reset_index()

    market_summary["Profit_Margin_Pct"] = (
        market_summary["Total_Profit"] / market_summary["Total_Sales"] * 100
    ).round(2)
    market_summary["Sales_Share_Pct"] = (
        market_summary["Total_Sales"] / market_summary["Total_Sales"].sum() * 100
    ).round(2)
    return market_summary.sort_values(by="Total_Sales", ascending=False)


def print_executive_kpi_card(kpis: Dict[str, Any]) -> None:
    """Format and print an executive KPI card with precise terminology."""
    divider = "=" * 65
    print("\n" + divider)
    print("      GLOBAL SUPERSTORE - EXECUTIVE KPI DASHBOARD")
    print(divider)
    print(f"  Total Revenue (Sales)          : ${kpis['total_sales']:>15,.2f}")
    print(f"  Total Net Profit               : ${kpis['total_profit']:>15,.2f}")
    print(f"  Overall Profit Margin          : {kpis['profit_margin_pct']:>15.2f}%")
    print(f"  Total Line Items (Transactions): {kpis['total_line_items']:>16,}")
    print(f"  Total Unique Orders            : {kpis['total_orders']:>16,}")
    print(f"  Total Unique Customers         : {kpis['total_customers']:>16,}")
    print(f"  Total Quantity Units Sold      : {kpis['total_quantity']:>16,}")
    print(f"  Average Order Value (AOV)      : ${kpis['avg_order_value']:>15,.2f}")
    print(f"  Average Profit per Order       : ${kpis['avg_profit_per_order']:>15,.2f}")
    print(f"  Average Shipping Cost          : ${kpis['avg_shipping_cost']:>15,.2f}")
    print(f"  Average Delivery Time          : {kpis['avg_shipping_days']:>15.2f} days")
    print(f"  Loss-Making Line Items         : {kpis['loss_making_line_items']:>12,} ({kpis['loss_making_line_items_pct']}%)")
    print(f"  Orders Containing Losses       : {kpis['orders_with_losses']:>12,} ({kpis['orders_with_losses_pct']}%)")
    print(f"  Orders with Net Negative Profit: {kpis['net_loss_orders']:>12,} ({kpis['net_loss_orders_pct']}%)")
    print(f"  Total Losses Incurred          : ${kpis['total_loss_amount']:>15,.2f}")
    print(divider + "\n")


if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_superstore.csv")
    kpis = compute_executive_kpis(df)
    print_executive_kpi_card(kpis)
