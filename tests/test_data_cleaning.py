"""
Unit Tests - Data Cleaning and Validation Pipeline
"""

import os
import pytest
import pandas as pd
from scripts.data_cleaning import load_raw_data, clean_superstore_data


@pytest.fixture(scope="module")
def raw_data():
    raw_path = "data/raw/superstore.csv"
    assert os.path.exists(raw_path), f"Raw dataset missing at {raw_path}"
    return load_raw_data(raw_path)


@pytest.fixture(scope="module")
def cleaned_tuple(raw_data):
    return clean_superstore_data(raw_data)


def test_raw_dataset_shape(raw_data):
    """Raw dataset must contain exactly 51,290 rows and 27 columns."""
    assert raw_data.shape == (51290, 27)


def test_cleaned_dataset_zero_nulls(cleaned_tuple):
    """Cleaned dataset must contain zero missing values."""
    df_clean, _ = cleaned_tuple
    assert df_clean.isnull().sum().sum() == 0


def test_artifact_column_dropped(cleaned_tuple):
    """Tableau artifact column '记录数' must be dropped."""
    df_clean, report = cleaned_tuple
    assert "记录数" not in df_clean.columns
    assert "记录数" in report["dropped_columns"]


def test_datetime_parsing(cleaned_tuple):
    """Order.Date and Ship.Date must be parsed as datetime64."""
    df_clean, _ = cleaned_tuple
    assert pd.api.types.is_datetime64_any_dtype(df_clean["Order.Date"])
    assert pd.api.types.is_datetime64_any_dtype(df_clean["Ship.Date"])


def test_shipping_days_validity(cleaned_tuple):
    """Shipping days must be non-negative (Ship.Date >= Order.Date)."""
    df_clean, _ = cleaned_tuple
    assert (df_clean["Shipping_Days"] >= 0).all()
    assert df_clean["Shipping_Days"].mean() > 0


def test_engineered_features_present(cleaned_tuple):
    """Verify presence of key operational and financial features."""
    df_clean, _ = cleaned_tuple
    expected_cols = [
        "Shipping_Days",
        "Profit_Margin_Pct",
        "Unit_Price",
        "Estimated_Cost",
        "YearMonth",
        "Discount_Band",
    ]
    for col in expected_cols:
        assert col in df_clean.columns, f"Missing engineered column: {col}"
