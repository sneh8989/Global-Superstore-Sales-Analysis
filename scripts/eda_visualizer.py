"""
Global Superstore Sales Analysis - Professional EDA & Visualization Suite
Module: scripts.eda_visualizer
Author: Sneh Kheni
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import pandas as pd
import numpy as np

# Apply professional, modern aesthetic
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 0.8,
    "grid.color": "#e5e5e5",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
    "figure.autolayout": False,
})

OUTPUT_DIR = "outputs/visuals"


def format_currency_millions(x, pos):
    """Format tick labels into Millions of dollars."""
    return f"${x*1e-6:.1f}M"


def format_currency_thousands(x, pos):
    """Format tick labels into Thousands of dollars."""
    return f"${x*1e-3:.0f}K"


def plot_monthly_timeline(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    """Plot 48-month continuous Sales and Profit timeline (2011-2014)."""
    df_copy = df.copy()
    if "YearMonth" not in df_copy.columns:
        df_copy["YearMonth"] = pd.to_datetime(df_copy["Order.Date"]).dt.to_period("M").astype(str)

    monthly = df_copy.groupby("YearMonth").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).sort_index()

    monthly["Sales_3M"] = monthly["Sales"].rolling(3).mean()
    monthly["Profit_3M"] = monthly["Profit"].rolling(3).mean()

    x = range(len(monthly))
    x_labels = monthly.index.tolist()

    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=300)

    # Sales bars
    bars = ax1.bar(x, monthly["Sales"], color="#3b82f6", alpha=0.5, label="Monthly Sales", width=0.7)
    ax1.plot(x, monthly["Sales_3M"], color="#1d4ed8", linewidth=2.2, label="Sales (3-Mo Moving Avg)")
    ax1.set_ylabel("Revenue (USD)", color="#1d4ed8", fontsize=11, fontweight="bold")
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_thousands))
    ax1.set_ylim(0, max(monthly["Sales"]) * 1.2)

    # Dual-axis Profit line
    ax2 = ax1.twinx()
    ax2.plot(x, monthly["Profit"], color="#10b981", marker="o", markersize=4, linewidth=1.5, label="Monthly Profit")
    ax2.plot(x, monthly["Profit_3M"], color="#047857", linewidth=2.0, linestyle="--", label="Profit (3-Mo Moving Avg)")
    ax2.set_ylabel("Net Profit (USD)", color="#047857", fontsize=11, fontweight="bold")
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_thousands))
    ax2.grid(False)

    # Formatting
    step = 4
    ax1.set_xticks(list(x)[::step])
    ax1.set_xticklabels(x_labels[::step], rotation=35, ha="right", fontsize=9)
    ax1.set_title("Global Superstore: 48-Month Sales & Profit Trajectory (2011 - 2014)", fontsize=14, fontweight="bold", pad=15)

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, framealpha=0.9)

    plt.tight_layout()
    path = os.path.join(output_dir, "01_monthly_sales_profit_trend.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_category_performance(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    """Plot Category revenue, profit, and margin comparison."""
    cat = df.groupby("Category").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    cat["Margin_Pct"] = (cat["Profit"] / cat["Sales"] * 100).round(1)
    cat = cat.sort_values(by="Sales", ascending=False)

    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)

    x = np.arange(len(cat))
    width = 0.35

    rects1 = ax1.bar(x - width/2, cat["Sales"], width, label="Sales", color="#2563eb", alpha=0.85)
    rects2 = ax1.bar(x + width/2, cat["Profit"], width, label="Profit", color="#10b981", alpha=0.85)

    ax1.set_ylabel("Amount (USD)", fontsize=11, fontweight="bold")
    ax1.set_title("Performance by Product Category: Sales vs. Profit", fontsize=13, fontweight="bold", pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(cat["Category"], fontsize=11, fontweight="semibold")
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_millions))
    ax1.legend(loc="upper right", frameon=True)

    # Annotate margin percentage
    for i, row in cat.reset_index().iterrows():
        sales_val = row["Sales"]
        profit_val = row["Profit"]
        margin = row["Margin_Pct"]
        ax1.annotate(f"${sales_val*1e-6:.2f}M", (i - width/2, sales_val + 70000), ha="center", fontsize=9, fontweight="bold")
        ax1.annotate(f"${profit_val*1e-6:.2f}M\n({margin}%)", (i + width/2, profit_val + 50000), ha="center", fontsize=8.5, color="#065f46")

    ax1.set_ylim(0, max(cat["Sales"]) * 1.15)
    plt.tight_layout()
    path = os.path.join(output_dir, "02_sales_profit_by_category.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_sub_category_profitability(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    """Plot Sub-Category profitability highlighting profit champions and loss makers."""
    sub = df.groupby(["Category", "Sub.Category"]).agg(
        Profit=("Profit", "sum"),
        Sales=("Sales", "sum")
    ).reset_index().sort_values(by="Profit", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)

    colors = ["#ef4444" if p < 0 else "#10b981" for p in sub["Profit"]]
    bars = ax.barh(sub["Sub.Category"], sub["Profit"], color=colors, alpha=0.85, height=0.65)

    ax.axvline(0, color="#6b7280", linewidth=1.0, linestyle="--")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_currency_thousands))
    ax.set_title("Profitability by Sub-Category (Red = Loss-Making, Green = Profitable)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Total Profit (USD)", fontsize=11, fontweight="bold")

    for bar in bars:
        width = bar.get_width()
        ha = "left" if width >= 0 else "right"
        offset = 4000 if width >= 0 else -4000
        ax.annotate(
            f"${width:,.0f}",
            (width + offset, bar.get_y() + bar.get_height() / 2),
            ha=ha, va="center", fontsize=8.5, fontweight="semibold"
        )

    ax.set_xlim(min(sub["Profit"]) * 1.25, max(sub["Profit"]) * 1.15)
    plt.tight_layout()
    path = os.path.join(output_dir, "03_sub_category_profitability.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_regional_performance(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    """Plot Sales and Profit by Global Region."""
    reg = df.groupby("Region").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values(by="Sales", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    y = np.arange(len(reg))
    height = 0.35

    ax.barh(y - height/2, reg["Sales"], height, label="Sales", color="#3b82f6", alpha=0.85)
    ax.barh(y + height/2, reg["Profit"], height, label="Profit", color="#10b981", alpha=0.85)

    ax.set_yticks(y)
    ax.set_yticklabels(reg["Region"], fontsize=10, fontweight="semibold")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_currency_millions))
    ax.set_title("Global Regional Performance: Sales vs. Profit", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Amount (USD)", fontsize=11, fontweight="bold")
    ax.legend(loc="lower right", frameon=True)

    plt.tight_layout()
    path = os.path.join(output_dir, "04_regional_performance.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_discount_elasticity(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    """Plot Discount Band vs Average Profit Margin % and Total Volume."""
    df_copy = df.copy()
    if "Discount_Band" not in df_copy.columns:
        discount_bins = [-0.01, 0.0, 0.10, 0.20, 0.30, 0.50, 1.0]
        discount_labels = ["0% (No Discount)", "1%-10%", "11%-20%", "21%-30%", "31%-50%", ">50%"]
        df_copy["Discount_Band"] = pd.cut(df_copy["Discount"], bins=discount_bins, labels=discount_labels)

    disc = df_copy.groupby("Discount_Band", observed=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Line_Item_Count=("Order.ID", "count"),
        Unique_Orders=("Order.ID", "nunique")
    ).reset_index()

    disc["Margin_Pct"] = (disc["Total_Profit"] / disc["Total_Sales"] * 100).round(1)

    fig, ax1 = plt.subplots(figsize=(11, 5.5), dpi=300)

    x = range(len(disc))
    colors = ["#10b981" if m >= 0 else "#ef4444" for m in disc["Margin_Pct"]]
    bars = ax1.bar(x, disc["Margin_Pct"], color=colors, alpha=0.85, width=0.55)
    ax1.axhline(0, color="#4b5563", linewidth=1.0)
    ax1.set_ylabel("Profit Margin (%)", fontsize=11, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(disc["Discount_Band"], fontsize=10, fontweight="semibold")
    ax1.set_title("The Discount Trap: Impact of Discounting on Profit Margin %", fontsize=13, fontweight="bold", pad=15)

    for bar in bars:
        h = bar.get_height()
        va = "bottom" if h >= 0 else "top"
        offset = 1.0 if h >= 0 else -2.5
        ax1.annotate(f"{h:.1f}%", (bar.get_x() + bar.get_width() / 2, h + offset), ha="center", va=va, fontsize=9.5, fontweight="bold")

    ax1.set_ylim(min(disc["Margin_Pct"]) * 1.25, max(disc["Margin_Pct"]) * 1.25)
    plt.tight_layout()
    path = os.path.join(output_dir, "05_discount_vs_profit_elasticity.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    # Also save backwards-compatible clean scatter plot with accurate line-item terminology
    plt.figure(figsize=(10, 6), dpi=300)
    plt.scatter(df["Discount"], df["Profit"], alpha=0.25, color="#2563eb", edgecolors="none", s=20)
    plt.axhline(0, color="#ef4444", linestyle="--", linewidth=1.2)
    plt.xlabel("Discount Rate (Decimal)", fontsize=11, fontweight="bold")
    plt.ylabel("Profit per Line Item (USD)", fontsize=11, fontweight="bold")
    plt.title("Discount vs. Profit Distribution (Individual Line Items)", fontsize=13, fontweight="bold", pad=15)
    plt.grid(True, linestyle="--", alpha=0.6)
    scatter_path = os.path.join(output_dir, "discount_profit_trend.png")
    plt.savefig(scatter_path, dpi=300, bbox_inches="tight")
    plt.close()

    return path


def plot_top_bottom_products(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    """Plot Top 10 Most Profitable vs Top 10 Loss-Making Products."""
    prod = df.groupby("Product.Name")["Profit"].sum().reset_index()
    top10 = prod.sort_values(by="Profit", ascending=False).head(10).sort_values(by="Profit", ascending=True)
    bottom10 = prod.sort_values(by="Profit", ascending=True).head(10).sort_values(by="Profit", ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    # Top 10
    ax1.barh(top10["Product.Name"], top10["Profit"], color="#10b981", alpha=0.85)
    ax1.set_title("Top 10 Most Profitable Products", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xlabel("Total Net Profit (USD)", fontsize=10, fontweight="bold")
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_currency_thousands))

    # Bottom 10
    ax2.barh(bottom10["Product.Name"], bottom10["Profit"], color="#ef4444", alpha=0.85)
    ax2.set_title("Top 10 Loss-Making Products (Critical Attention Required)", fontsize=12, fontweight="bold", pad=10)
    ax2.set_xlabel("Total Loss Incurred (USD)", fontsize=10, fontweight="bold")
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_currency_thousands))

    plt.tight_layout()
    path = os.path.join(output_dir, "06_top_bottom_products.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def plot_customer_segments(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> str:
    """Plot Customer Segment revenue and profit distribution."""
    seg = df.groupby("Segment").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    colors = ["#3b82f6", "#10b981", "#f59e0b"]

    ax1.pie(seg["Sales"], labels=seg["Segment"], autopct="%1.1f%%", startangle=140, colors=colors, explode=(0.04, 0, 0))
    ax1.set_title("Sales Share by Customer Segment", fontsize=12, fontweight="bold")

    ax2.pie(seg["Profit"], labels=seg["Segment"], autopct="%1.1f%%", startangle=140, colors=colors, explode=(0.04, 0, 0))
    ax2.set_title("Profit Share by Customer Segment", fontsize=12, fontweight="bold")

    plt.tight_layout()
    path = os.path.join(output_dir, "07_customer_segment_distribution.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def generate_all_visuals(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> list:
    """Generate all visualizations and save to disk."""
    os.makedirs(output_dir, exist_ok=True)
    paths = [
        plot_monthly_timeline(df, output_dir),
        plot_category_performance(df, output_dir),
        plot_sub_category_profitability(df, output_dir),
        plot_regional_performance(df, output_dir),
        plot_discount_elasticity(df, output_dir),
        plot_top_bottom_products(df, output_dir),
        plot_customer_segments(df, output_dir),
    ]
    return paths


if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_superstore.csv")
    print(f"Generating publication visuals in '{OUTPUT_DIR}'...")
    saved_paths = generate_all_visuals(df)
    print(f"Generated {len(saved_paths)} visualizations successfully!")
    for p in saved_paths:
        print(f"  - {p}")
