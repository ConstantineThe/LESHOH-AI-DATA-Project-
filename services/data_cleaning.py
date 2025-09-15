import pandas as pd
import numpy as np
import re
from datetime import datetime
from .config import PRODUCT_MAPPING

def clean_data(df):
    """
    The main cleaning function. Applies all cleaning steps to the input DataFrame.
    Returns a new, cleaned DataFrame.
    """
    cleaned_df = df.copy()
    print("\nStarting data cleaning process...")
    initial_count = len(cleaned_df)

    cleaned_df = _handle_missing_values(cleaned_df)
    cleaned_df = _normalize_product_names(cleaned_df)
    cleaned_df = _standardize_dates(cleaned_df)
    cleaned_df = _remove_duplicates(cleaned_df)
    cleaned_df = _handle_outliers(cleaned_df)

    # Ensure final data types are correct
    cleaned_df['quantity'] = cleaned_df['quantity'].astype(int)
    cleaned_df['price_per_unit'] = cleaned_df['price_per_unit'].astype(float)
    cleaned_df['total_price'] = cleaned_df['total_price'].astype(float)

    print(f"\n=== CLEANING SUMMARY ===")
    print(f"Rows removed: {initial_count - len(cleaned_df)}")
    print(f"Final dataset shape: {cleaned_df.shape}")
    print("\nMissing values after cleaning:")
    print(cleaned_df.isnull().sum())

    return cleaned_df

def _handle_missing_values(df):
    """Handles missing values in price, quantity, and total_price."""
    print("\n1. Handling missing values...")
    initial_count = len(df)

    # Price per unit missing: price_per_unit = total_price / quantity
    mask_p = df["price_per_unit"].isna() & df["quantity"].notna() & df["total_price"].notna()
    df.loc[mask_p, "price_per_unit"] = (
        df.loc[mask_p, "total_price"] / df.loc[mask_p, "quantity"]
    )

    # Quantity missing: quantity = total_price / price_per_unit
    mask_q = df["quantity"].isna() & df["price_per_unit"].notna() & df["total_price"].notna()
    df.loc[mask_q, "quantity"] = (
        df.loc[mask_q, "total_price"] / df.loc[mask_q, "price_per_unit"]
    )

    # Total price missing: total_price = quantity * price_per_unit
    mask_t = df["total_price"].isna() & df["quantity"].notna() & df["price_per_unit"].notna()
    df.loc[mask_t, "total_price"] = (
        df.loc[mask_t, "quantity"] * df.loc[mask_t, "price_per_unit"]
    )

    # Remove rows where critical data is still missing
    df = df.dropna(subset=['price_per_unit', 'quantity', 'total_price'])
    print(f"Removed {initial_count - len(df)} rows with missing critical data")

    return df

def _normalize_product_names(df):
    """Normalizes inconsistent product names."""
    print("\n2. Normalizing product names...")

    # First, clean whitespace and convert to lowercase
    df['product_name'] = df['product_name'].str.strip().str.lower()

    def normalize_product_name(name):
        for pattern, replacement in PRODUCT_MAPPING.items():
            if re.search(pattern, name, re.IGNORECASE):
                return replacement
        return name.title()  # Capitalize first letter of each word as fallback

    df['product_name'] = df['product_name'].apply(normalize_product_name)
    print("Product names after normalization:")
    print(df['product_name'].value_counts())

    return df

def _standardize_dates(df):
    """Standardizes various date formats into YYYY-MM-DD."""
    print("\n3. Standardizing dates...")

    def parse_date(date_str):
        # Handle invalid dates and different formats
        if pd.isna(date_str) or date_str == 'Invalid Date':
            return np.nan

        # Convert to string first
        date_str = str(date_str)

        # Try different date formats
        formats = [
            '%Y-%m-%d',    # 2025-03-09
            '%Y/%m/%d',    # 2025/03/09
            '%d/%m/%Y',    # 09/03/2025
            '%m/%d/%Y',    # 03/09/2025
            '%B %d, %Y',   # March 09, 2025
            '%d-%m-%y',    # 09-03-25
            '%m/%d/%y',    # 03/09/25 (for dates like 07/02/2025)
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # Check if year is reasonable (not in distant past/future)
                if 1900 <= parsed_date.year <= 2030:
                    return parsed_date.date()
            except ValueError:
                continue

        return np.nan  # Return NaN if all formats fail

    df['transaction_date'] = df['transaction_date'].apply(parse_date)

    # Remove rows with invalid dates
    initial_count = len(df)
    df = df.dropna(subset=['transaction_date'])
    print(f"Removed {initial_count - len(df)} rows with invalid dates")

    return df

def _remove_duplicates(df):
    """Removes duplicate rows from the dataset."""
    print("\n4. Removing duplicates...")
    initial_count = len(df)

    # Keep first occurrence of duplicates based on all columns except transaction_id
    df = df.drop_duplicates(subset=df.columns.difference(['transaction_id']))
    print(f"Removed {initial_count - len(df)} duplicate rows")

    return df

def _handle_outliers(df):
    """Fixes outliers and mismatches between quantity, price, and total."""
    print("\n5. Handling outliers and mismatches...")
    initial_count = len(df)

    # Find mismatches with tolerance (absolute difference < 0.01)
    mismatches = ~np.isclose(
        df["total_price"],
        df["quantity"] * df["price_per_unit"],
        rtol=0,
        atol=0.01
    )

    # Extract mismatch rows
    mismatch_rows = df[mismatches]
    print(f"Found {len(mismatch_rows)} mismatches:")

    # Handle conflicts
    conflict_mask = mismatches & (df["quantity"] > 100) & (df["price_per_unit"] > 1000)
    if conflict_mask.any():
        print(f"Resolving {conflict_mask.sum()} conflicting rows (both q>100 and p>1000) by adjusting quantity.")
        df.loc[conflict_mask, "quantity"] = (
            df.loc[conflict_mask, "total_price"] / df.loc[conflict_mask, "price_per_unit"]
        )

    # Fix quantity if it's too large (>100)
    mask_q = mismatches & (df["quantity"] > 100) & ~conflict_mask
    df.loc[mask_q, "quantity"] = (
        df.loc[mask_q, "total_price"] / df.loc[mask_q, "price_per_unit"]
    )

    # Fix price_per_unit if it's too large (>1000)
    mask_p = mismatches & (df["price_per_unit"] > 1000) & ~conflict_mask
    df.loc[mask_p, "price_per_unit"] = (
        df.loc[mask_p, "total_price"] / df.loc[mask_p, "quantity"]
    )

    # Otherwise fix total_price
    mask_t = mismatches & ~(mask_q | mask_p | conflict_mask)
    df.loc[mask_t, "total_price"] = (
        df.loc[mask_t, "quantity"] * df.loc[mask_t, "price_per_unit"]
    )

    # Round values consistently
    df["quantity"] = df["quantity"].round(0).astype("Int64")
    df["price_per_unit"] = df["price_per_unit"].round(2)
    df["total_price"] = df["total_price"].round(2)

    # Recheck mismatches with tolerance
    final_check = ~np.isclose(
        df["total_price"],
        df["quantity"] * df["price_per_unit"],
        rtol=0,
        atol=0.01
    )

    print(f"Remaining mismatches after adjustment: {final_check.sum()}")
    print(f"Removed {initial_count - len(df)} outlier rows")

    return df