# scripts/docker_load_data.py
"""
Loads all CSVs into the Docker PostgreSQL container.
Run this AFTER docker-compose up succeeds.

Usage:
    python scripts/docker_load_data.py
"""

import pandas as pd
from sqlalchemy import create_engine, text
from io import StringIO
import time
import os

# Docker PostgreSQL is on port 5433 (mapped from container's 5432)
DB_URL = "postgresql+psycopg2://postgres:{password}@localhost:5433/social_media_analytics"

RAW_DATA_PATH = "data/raw"

LOAD_ORDER = [
    {"file": "platforms.csv",         "table": "platforms",         "parse_dates": []},
    {"file": "calendar.csv",          "table": "calendar",          "parse_dates": ["date"],
     "fill_nulls": {"sales_event": "No Event"}},
    {"file": "businesses.csv",        "table": "businesses",        "parse_dates": []},
    {"file": "customers.csv",         "table": "customers",         "parse_dates": []},
    {"file": "campaigns.csv",         "table": "campaigns",         "parse_dates": ["start_date", "end_date"]},
    {"file": "engagement_metrics.csv","table": "engagement_metrics","parse_dates": []},
    {"file": "conversions.csv",       "table": "conversions",       "parse_dates": ["conversion_date"]},
]


def copy_to_table(df, table, engine):
    buf = StringIO()
    df.to_csv(buf, index=False, header=False)
    buf.seek(0)
    with engine.connect() as conn:
        raw = conn.connection
        with raw.cursor() as cur:
            cur.copy_expert(
                f"COPY {table} ({','.join(df.columns)}) FROM STDIN WITH (FORMAT CSV, NULL '')",
                buf,
            )
        raw.commit()


def run():
    # Read password from .env
    from dotenv import load_dotenv
    load_dotenv()
    password = os.getenv("DB_PASSWORD", "")

    url = DB_URL.format(password=password)
    engine = create_engine(url)

    print("\n" + "=" * 55)
    print("  DOCKER ETL LOAD")
    print("=" * 55)

    # Clear existing data
    print("\n🧹 Clearing existing data...")
    with engine.connect() as conn:
        conn.execute(text("""
            TRUNCATE TABLE conversions, engagement_metrics, campaigns,
                           customers, businesses, calendar, platforms
            RESTART IDENTITY CASCADE
        """))
        conn.commit()

    total = 0
    for config in LOAD_ORDER:
        filepath = os.path.join(RAW_DATA_PATH, config["file"])
        print(f"\n  📂 {config['file']} → [{config['table']}]")
        start = time.time()

        df = pd.read_csv(
            filepath,
            parse_dates=config["parse_dates"] or False,
        )
        for col, val in config.get("fill_nulls", {}).items():
            df[col] = df[col].fillna(val)
        for col in config["parse_dates"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")

        copy_to_table(df, config["table"], engine)
        elapsed = time.time() - start
        print(f"     ✅ {len(df):,} rows in {elapsed:.1f}s")
        total += len(df)

    print(f"\n{'='*55}")
    print(f"  ✅ DONE — {total:,} total rows loaded into Docker DB")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    run()