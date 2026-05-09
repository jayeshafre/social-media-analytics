# scripts/validate_data.py
"""
Data Validation Script
Runs integrity checks on all raw CSVs before loading to PostgreSQL.
"""

import pandas as pd
import os

RAW_DATA_PATH = "data/raw"

EXPECTED_ROWS = {
    "platforms.csv": 5,
    "calendar.csv": 2192,
    "businesses.csv": 5000,
    "customers.csv": 500000,
    "campaigns.csv": 200000,
    "engagement_metrics.csv": 1099493,
    "conversions.csv": 855533,
}

PRIMARY_KEYS = {
    "platforms.csv": "platform_id",
    "calendar.csv": "date",
    "businesses.csv": "business_id",
    "customers.csv": "customer_id",
    "campaigns.csv": "campaign_id",
    "engagement_metrics.csv": "engagement_id",
    "conversions.csv": "conversion_id",
}


def validate_all():
    print("\n" + "=" * 60)
    print("  DATA VALIDATION REPORT")
    print("=" * 60)

    all_passed = True

    for filename, expected in EXPECTED_ROWS.items():
        filepath = os.path.join(RAW_DATA_PATH, filename)
        print(f"\n📄 {filename}")

        # Load
        df = pd.read_csv(filepath)

        # Row count check
        actual = len(df)
        row_status = "✅" if actual == expected else "❌"
        print(f"   Rows     : {actual:,} / {expected:,} {row_status}")
        if actual != expected:
            all_passed = False

        # Duplicate PK check
        pk = PRIMARY_KEYS[filename]
        dupes = df[pk].duplicated().sum()
        pk_status = "✅" if dupes == 0 else "❌"
        print(f"   Duplicate PKs ({pk}): {dupes} {pk_status}")
        if dupes > 0:
            all_passed = False

        # Null check (excluding known nullable columns)
        nullable_cols = ["sales_event"]
        check_cols = [c for c in df.columns if c not in nullable_cols]
        nulls = df[check_cols].isnull().sum().sum()
        null_status = "✅" if nulls == 0 else "⚠️"
        print(f"   Nulls (excl. nullable cols): {nulls} {null_status}")

    print("\n" + "=" * 60)
    if all_passed:
        print("  ✅ ALL CHECKS PASSED — Data is ready for PostgreSQL load")
    else:
        print("  ❌ SOME CHECKS FAILED — Review errors above before loading")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    validate_all()