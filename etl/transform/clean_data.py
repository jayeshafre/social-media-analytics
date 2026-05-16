# etl/transform/clean_data.py
"""
ETL Transform Layer — Phase 5
Cleans and validates raw CSVs before loading into PostgreSQL.

Pipeline:
    data/raw/  →  [clean_data.py]  →  data/processed/

Run standalone:
    python etl/transform/clean_data.py
"""

import pandas as pd
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("etl_transform")

RAW_PATH       = "data/raw"
PROCESSED_PATH = "data/processed"

os.makedirs(PROCESSED_PATH, exist_ok=True)


# ─────────────────────────────────────────
# TRANSFORM FUNCTIONS
# One function per table — keeps logic isolated
# ─────────────────────────────────────────

def clean_platforms(df: pd.DataFrame) -> pd.DataFrame:
    """Platform dimension — small table, minimal cleaning needed."""
    logger.info("  Cleaning platforms...")
    df.columns = df.columns.str.strip().str.lower()
    df = df.drop_duplicates(subset=["platform_id"])
    assert len(df) == 5, f"Expected 5 platforms, got {len(df)}"
    return df


def clean_calendar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calendar dimension.
    Key transform: fill NaN sales_event with 'No Event'.
    """
    logger.info("  Cleaning calendar...")
    df.columns = df.columns.str.strip().str.lower()
    df["date"]         = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["is_weekend"]   = df["is_weekend"].astype(bool)
    df["sales_event"]  = df["sales_event"].fillna("No Event")
    df = df.drop_duplicates(subset=["date"])
    return df


def clean_businesses(df: pd.DataFrame) -> pd.DataFrame:
    """Business dimension — standardise text fields."""
    logger.info("  Cleaning businesses...")
    df.columns = df.columns.str.strip().str.lower()
    df["business_name"]     = df["business_name"].str.strip()
    df["business_category"] = df["business_category"].str.strip()
    df["is_influencer_brand"] = df["is_influencer_brand"].astype(bool)
    df = df.drop_duplicates(subset=["business_id"])

    # Validate profit margin is between 0 and 1
    invalid_margin = df[
        (df["avg_profit_margin"] < 0) | (df["avg_profit_margin"] > 1)
    ]
    if len(invalid_margin) > 0:
        logger.warning(f"  ⚠️  {len(invalid_margin)} rows with invalid profit margin — clamping to [0,1]")
        df["avg_profit_margin"] = df["avg_profit_margin"].clip(0, 1)

    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Customer dimension — validate age groups and income levels."""
    logger.info("  Cleaning customers...")
    df.columns = df.columns.str.strip().str.lower()
    df["is_mobile_first"] = df["is_mobile_first"].astype(bool)

    valid_age_groups = {"18-24", "25-34", "35-44", "45-54", "55+"}
    invalid_age = df[~df["age_group"].isin(valid_age_groups)]
    if len(invalid_age) > 0:
        logger.warning(f"  ⚠️  {len(invalid_age)} rows with unexpected age groups")

    # Clamp negative purchase values
    neg_purchase = (df["avg_purchase_value"] < 0).sum()
    if neg_purchase > 0:
        logger.warning(f"  ⚠️  {neg_purchase} rows with negative avg_purchase_value — setting to 0")
        df["avg_purchase_value"] = df["avg_purchase_value"].clip(lower=0)

    df = df.drop_duplicates(subset=["customer_id"])
    return df


def clean_campaigns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Core fact table — most important transform.
    Key decisions:
      - 674 rows with roas=0 are VALID (brand awareness / no direct revenue)
      - Remove any future dates beyond 2024 (out of calendar range)
    """
    logger.info("  Cleaning campaigns...")
    df.columns = df.columns.str.strip().str.lower()

    df["start_date"]      = pd.to_datetime(df["start_date"])
    df["end_date"]        = pd.to_datetime(df["end_date"])
    df["influencer_used"] = df["influencer_used"].astype(bool)

    # Remove campaigns with start_date beyond 2024 (calendar boundary)
    before = len(df)
    df = df[df["start_date"].dt.year <= 2024]
    removed = before - len(df)
    if removed > 0:
        logger.warning(f"  ⚠️  Removed {removed} campaigns with start_date > 2024")

    # Format dates as strings for DB
    df["start_date"] = df["start_date"].dt.strftime("%Y-%m-%d")
    df["end_date"]   = df["end_date"].dt.strftime("%Y-%m-%d")

    # Validate key numeric ranges
    assert (df["ctr"] >= 0).all(),              "Negative CTR found"
    assert (df["cpc"] >= 0).all(),              "Negative CPC found"
    assert (df["sentiment_score"] >= 0).all(),  "Negative sentiment found"
    assert (df["sentiment_score"] <= 1).all(),  "Sentiment > 1 found"

    df = df.drop_duplicates(subset=["campaign_id"])

    logger.info(f"  ℹ️  {(df['roas']==0).sum()} campaigns with roas=0 retained (valid brand awareness campaigns)")
    return df


def clean_engagement_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Engagement satellite fact — validate snapshot sequence."""
    logger.info("  Cleaning engagement_metrics...")
    df.columns = df.columns.str.strip().str.lower()

    # Snapshot numbers should be 1–7
    invalid_snap = df[
        (df["snapshot_number"] < 1) | (df["snapshot_number"] > 7)
    ]
    if len(invalid_snap) > 0:
        logger.warning(f"  ⚠️  {len(invalid_snap)} rows with snapshot_number out of range 1–7")

    # Clamp negative watch_time
    neg_watch = (df["watch_time_seconds"] < 0).sum()
    if neg_watch > 0:
        logger.warning(f"  ⚠️  {neg_watch} rows with negative watch_time_seconds — setting to 0")
        df["watch_time_seconds"] = df["watch_time_seconds"].clip(lower=0)

    df = df.drop_duplicates(subset=["engagement_id"])
    return df


def clean_conversions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conversion satellite fact.
    Key transform: remove rows with conversion_date > 2024-12-31
    (outside calendar range — identified in Phase 4).
    """
    logger.info("  Cleaning conversions...")
    df.columns = df.columns.str.strip().str.lower()

    df["conversion_date"]  = pd.to_datetime(df["conversion_date"])
    df["discount_used"]    = df["discount_used"].astype(bool)
    df["repeat_customer"]  = df["repeat_customer"].astype(bool)

    # Remove 2025 rows (outside calendar range)
    before = len(df)
    df = df[df["conversion_date"].dt.year <= 2024]
    removed = before - len(df)
    if removed > 0:
        logger.info(f"  ✂️  Removed {removed} conversions with date > 2024 (outside calendar range)")

    df["conversion_date"] = df["conversion_date"].dt.strftime("%Y-%m-%d")

    # Validate discount_pct
    valid_discounts = {0, 5, 10, 15, 20, 25}
    invalid_disc = df[~df["discount_pct"].isin(valid_discounts)]
    if len(invalid_disc) > 0:
        logger.warning(f"  ⚠️  {len(invalid_disc)} rows with unexpected discount_pct values")

    df = df.drop_duplicates(subset=["conversion_id"])
    return df


# ─────────────────────────────────────────
# PIPELINE RUNNER
# ─────────────────────────────────────────
PIPELINE = [
    ("platforms.csv",         "platforms.csv",         clean_platforms),
    ("calendar.csv",          "calendar.csv",           clean_calendar),
    ("businesses.csv",        "businesses.csv",         clean_businesses),
    ("customers.csv",         "customers.csv",          clean_customers),
    ("campaigns.csv",         "campaigns.csv",          clean_campaigns),
    ("engagement_metrics.csv","engagement_metrics.csv", clean_engagement_metrics),
    ("conversions.csv",       "conversions.csv",        clean_conversions),
]


def run_transform():
    logger.info("\n" + "="*55)
    logger.info("  ETL TRANSFORM — Clean Raw → Processed")
    logger.info("="*55)

    for raw_file, out_file, transform_fn in PIPELINE:
        raw_path  = os.path.join(RAW_PATH, raw_file)
        out_path  = os.path.join(PROCESSED_PATH, out_file)

        logger.info(f"\n📂 {raw_file}")

        df = pd.read_csv(raw_path)
        logger.info(f"  Raw rows: {len(df):,}")

        df_clean = transform_fn(df)
        logger.info(f"  Clean rows: {len(df_clean):,}")

        df_clean.to_csv(out_path, index=False)
        logger.info(f"  ✅ Saved → {out_path}")

    logger.info("\n" + "="*55)
    logger.info("  TRANSFORM COMPLETE — check data/processed/")
    logger.info("="*55 + "\n")


if __name__ == "__main__":
    run_transform()