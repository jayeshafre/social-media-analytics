# etl/load/load_csv_to_postgres.py
"""
ETL Load Script — Phase 4
Uses PostgreSQL COPY command for fast, reliable bulk loading.
No parameter limit issues. Industry standard approach.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import time
from io import StringIO

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "social_media_analytics")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "")

RAW_DATA_PATH = "data/raw"

LOAD_ORDER = [
    {
        "file": "platforms.csv",
        "table": "platforms",
        "type": "dimension",
    },
    {
        "file": "calendar.csv",
        "table": "calendar",
        "type": "dimension",
        "fill_nulls": {"sales_event": "No Event"},
        "parse_dates": ["date"],
    },
    {
        "file": "businesses.csv",
        "table": "businesses",
        "type": "dimension",
    },
    {
        "file": "customers.csv",
        "table": "customers",
        "type": "dimension",
    },
    {
        "file": "campaigns.csv",
        "table": "campaigns",
        "type": "fact",
        "parse_dates": ["start_date", "end_date"],
    },
    {
        "file": "engagement_metrics.csv",
        "table": "engagement_metrics",
        "type": "fact",
    },
    {
        "file": "conversions.csv",
        "table": "conversions",
        "type": "fact",
        "parse_dates": ["conversion_date"],
    },
]


def get_engine():
    connection_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return create_engine(connection_string)


def test_connection(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful\n")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def copy_df_to_table(df, table_name, engine):
    """
    Load a DataFrame into PostgreSQL using the COPY command.
    
    Why COPY instead of INSERT?
    - No parameter limit (65,535 cap doesn't apply)
    - Streams data as a CSV buffer — no huge SQL statements
    - 10-20x faster than multi-row INSERT for large tables
    - Used by production data engineers at scale
    """
    # Write DataFrame to an in-memory CSV buffer
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)  # rewind to start of buffer

    # Get the raw psycopg2 connection from SQLAlchemy
    with engine.connect() as conn:
        raw_conn = conn.connection

        with raw_conn.cursor() as cursor:
            cursor.copy_expert(
                sql=f"""
                    COPY {table_name} ({', '.join(df.columns)})
                    FROM STDIN
                    WITH (FORMAT CSV, NULL '')
                """,
                file=buffer,
            )
        raw_conn.commit()


def load_table(config, engine):
    filepath = os.path.join(RAW_DATA_PATH, config["file"])
    table_name = config["table"]
    fill_nulls = config.get("fill_nulls", {})
    parse_dates = config.get("parse_dates", [])

    print(f"  📂 Loading {config['file']} → [{table_name}]")
    start = time.time()

    # Read CSV
    df = pd.read_csv(
        filepath,
        parse_dates=parse_dates if parse_dates else False
    )

    # Fill nulls where specified
    for col, val in fill_nulls.items():
        df[col] = df[col].fillna(val)

    # Format date columns as plain date strings (COPY needs clean format)
    for col in parse_dates:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")

    total_rows = len(df)

    # Use COPY for all tables
    copy_df_to_table(df, table_name, engine)

    elapsed = time.time() - start
    print(f"     ✅ {total_rows:,} rows loaded in {elapsed:.1f}s")
    return total_rows


def run_etl():
    print("\n" + "=" * 55)
    print("  ETL LOAD — Social Media Analytics Platform")
    print("=" * 55)

    engine = get_engine()
    if not test_connection(engine):
        return

    # Clear existing data before reloading (safe re-run)
    print("🧹 Clearing existing data...\n")
    with engine.connect() as conn:
        conn.execute(text("""
            TRUNCATE TABLE conversions, engagement_metrics, campaigns,
                           customers, businesses, calendar, platforms
            RESTART IDENTITY CASCADE
        """))
        conn.commit()

    total_rows_loaded = 0
    failed = []

    for config in LOAD_ORDER:
        print(f"\n[{config['type'].upper()}]")
        try:
            rows = load_table(config, engine)
            total_rows_loaded += rows
        except Exception as e:
            print(f"     ❌ FAILED: {e}")
            failed.append(config["table"])

    print("\n" + "=" * 55)
    print(f"  LOAD COMPLETE")
    print(f"  Total rows loaded : {total_rows_loaded:,}")
    print(f"  Tables failed     : {len(failed)}")
    if failed:
        print(f"  Failed tables     : {', '.join(failed)}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    run_etl()