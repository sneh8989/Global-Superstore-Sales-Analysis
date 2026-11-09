"""
Global Superstore Sales Analysis - Enterprise Excel & Pivot Table Exporter
Module: scripts.pivot_exporter
Author: Sneh Kheni
"""

import os
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def format_worksheet(ws, title: str):
    """Apply corporate styling to an openpyxl worksheet."""
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9")
    )
    
    # Format header row (row 1)
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    # Format data rows
    for row in range(2, ws.max_row + 1):
        is_even = (row % 2 == 0)
        row_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid") if is_even else None
        for col in range(1, ws.max_column + 1):
            cell = ws.cell(row=row, column=col)
            cell.font = data_font
            cell.border = thin_border
            if row_fill and not cell.fill.start_color.rgb:
                cell.fill = row_fill
                
            # Number formatting
            if isinstance(cell.value, (int, float)):
                if abs(cell.value) >= 1000:
                    cell.number_format = "#,##0.00"
                elif isinstance(cell.value, float):
                    cell.number_format = "#,##0.00"
                else:
                    cell.number_format = "#,##0"
                    
    # Auto-adjust column widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)


def export_all_pivot_tables_and_reports(df: pd.DataFrame, base_dir: str = None) -> dict:
    """Generate individual pivot tables and an all-in-one executive workbook."""
    if base_dir is None:
        if os.path.exists("outputs"):
            base_dir = "."
        elif os.path.exists("../outputs"):
            base_dir = ".."
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            
    pivot_dir = os.path.join(base_dir, "outputs", "pivot_tables")
    reports_dir = os.path.join(base_dir, "outputs", "reports")
    os.makedirs(pivot_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # 1. Sales by Category & Segment
    sales_cat_seg = pd.pivot_table(
        df, index="Category", columns="Segment", values="Sales", aggfunc="sum", margins=True, margins_name="Total"
    )
    sales_cat_seg_path = os.path.join(pivot_dir, "sales_by_category_segment.xlsx")
    sales_cat_seg.to_excel(sales_cat_seg_path)
    
    # 2. Profit by Category & Segment
    profit_cat_seg = pd.pivot_table(
        df, index="Category", columns="Segment", values="Profit", aggfunc="sum", margins=True, margins_name="Total"
    )
    profit_cat_seg_path = os.path.join(pivot_dir, "profit_by_category_segment.xlsx")
    profit_cat_seg.to_excel(profit_cat_seg_path)
    
    # 3. Profit by Region & Category
    profit_reg_cat = pd.pivot_table(
        df, index="Region", columns="Category", values="Profit", aggfunc="sum", margins=True, margins_name="Total"
    )
    profit_reg_cat_path = os.path.join(pivot_dir, "profit_by_region_category.xlsx")
    profit_reg_cat.to_excel(profit_reg_cat_path)
    
    # 4. Profit by Market & Category
    profit_mkt_cat = pd.pivot_table(
        df, index="Market", columns="Category", values="Profit", aggfunc="sum", margins=True, margins_name="Total"
    )
    profit_mkt_cat_path = os.path.join(pivot_dir, "profit_by_market_category.xlsx")
    profit_mkt_cat.to_excel(profit_mkt_cat_path)
    
    # 5. Master Multi-Tab Executive Report
    master_path = os.path.join(reports_dir, "global_superstore_executive_report.xlsx")
    with pd.ExcelWriter(master_path, engine="openpyxl") as writer:
        # Tab 1: Category & Segment Sales
        sales_cat_seg.reset_index().to_excel(writer, sheet_name="Sales_Category_Segment", index=False)
        # Tab 2: Category & Segment Profit
        profit_cat_seg.reset_index().to_excel(writer, sheet_name="Profit_Category_Segment", index=False)
        # Tab 3: Regional Performance
        profit_reg_cat.reset_index().to_excel(writer, sheet_name="Profit_Region_Category", index=False)
        # Tab 4: Market Performance
        profit_mkt_cat.reset_index().to_excel(writer, sheet_name="Profit_Market_Category", index=False)
        
        # Tab 5: Discount Impact
        disc_summary = df.groupby("Discount_Band", observed=False).agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Orders=("Order.ID", "nunique"),
            Avg_Shipping_Cost=("Shipping.Cost", "mean")
        ).reset_index()
        disc_summary["Profit_Margin_Pct"] = (
            disc_summary["Total_Profit"] / disc_summary["Total_Sales"] * 100
        ).round(2)
        disc_summary.to_excel(writer, sheet_name="Discount_Impact_Analysis", index=False)
        
        # Tab 6: Yearly Trends
        yearly = df.groupby("Year").agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Orders=("Order.ID", "nunique"),
            Total_Quantity=("Quantity", "sum")
        ).sort_index().reset_index()
        yearly["YoY_Sales_Growth_%"] = (yearly["Total_Sales"].pct_change() * 100).round(2)
        yearly["YoY_Profit_Growth_%"] = (yearly["Total_Profit"].pct_change() * 100).round(2)
        yearly["Profit_Margin_%"] = (yearly["Total_Profit"] / yearly["Total_Sales"] * 100).round(2)
        yearly.to_excel(writer, sheet_name="Yearly_Trends", index=False)

    # Apply openpyxl styling to each sheet
    import openpyxl
    wb = openpyxl.load_workbook(master_path)
    for sheet_name in wb.sheetnames:
        format_worksheet(wb[sheet_name], sheet_name)
    wb.save(master_path)
    
    return {
        "master_report": master_path,
        "pivot_tables": [
            sales_cat_seg_path,
            profit_cat_seg_path,
            profit_reg_cat_path,
            profit_mkt_cat_path,
        ]
    }


if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_superstore.csv")
    print("Exporting pivot tables and executive report...")
    res = export_all_pivot_tables_and_reports(df)
    print(f"Master Executive Report created at: {res['master_report']}")
    print(f"Individual Pivot Tables created: {len(res['pivot_tables'])}")
