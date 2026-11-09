"""
Global Superstore Sales Analysis - Reusable Analysis & Data Engineering Package
"""

from .data_cleaning import clean_superstore_data, load_raw_data, save_cleaned_data
from .kpi_engine import compute_executive_kpis, compute_category_kpis, compute_segment_kpis, compute_market_kpis
from .time_series import analyze_yearly_trends, analyze_monthly_continuous_trends, analyze_quarterly_trends, calculate_cagr
from .eda_visualizer import generate_all_visuals
from .pivot_exporter import export_all_pivot_tables_and_reports

__all__ = [
    "clean_superstore_data",
    "load_raw_data",
    "save_cleaned_data",
    "compute_executive_kpis",
    "compute_category_kpis",
    "compute_segment_kpis",
    "compute_market_kpis",
    "analyze_yearly_trends",
    "analyze_monthly_continuous_trends",
    "analyze_quarterly_trends",
    "calculate_cagr",
    "generate_all_visuals",
    "export_all_pivot_tables_and_reports",
]
