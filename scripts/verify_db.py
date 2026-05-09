# scripts/verify_db.py
"""
Verifies that all tables were loaded correctly into PostgreSQL.
Run this after load_csv_to_postgres.py to confirm row counts.
"""

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    f"/{os.getenv('DB_NAME')}"
)

EXPECTED = {
    "platforms": 5,
    "calendar": 2192,
    "businesses": 5000,
    "customers": 500000,
    "campaigns": 200000,
    "engagement_metrics": 1099493,
    "conversions": 846511,
}


def verify():
    engine = create_engine(DB_URL)
    print("\n" + "=" * 55)
    print("  DATABASE VERIFICATION REPORT")
    print("=" * 55)

    all_ok = True
    with engine.connect() as conn:
        for table, expected in EXPECTED.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            actual = result.scalar()
            status = "✅" if actual == expected else "❌"
            print(f"  {status}  {table:<25} {actual:>10,} / {expected:>10,}")
            if actual != expected:
                all_ok = False

    print("=" * 55)
    print(f"  {'✅ ALL TABLES VERIFIED' if all_ok else '❌ MISMATCH FOUND — CHECK ABOVE'}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    verify()