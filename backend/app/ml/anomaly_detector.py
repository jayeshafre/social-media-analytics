"""
Statistical Anomaly Detector — Phase 8.

Uses Isolation Forest to detect statistically unusual months
in your KPI history without needing labeled training data.

Why Isolation Forest:
- Unsupervised — no need to label anomalies manually
- Works well with small datasets (72 months)
- Fast and interpretable
- Industry standard for time-series anomaly detection

Anomaly score interpretation:
- Score close to -1 → highly anomalous
- Score close to 0  → borderline
- Score close to +1 → normal
"""

import logging
import numpy as np
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("sma_api.anomaly_detector")


# ─────────────────────────────────────────────────────────────
# Data fetcher
# ─────────────────────────────────────────────────────────────
def _fetch_monthly_data(
    db:       Session,
    platform: Optional[str] = None,
) -> list[dict]:
    """Fetch monthly KPI data for anomaly detection."""
    plat_filter = "AND cam.platform = :platform" if platform else ""
    params      = {"platform": platform} if platform else {}

    query = text(f"""
        SELECT
            c.year,
            c.month,
            (c.year * 12 + c.month)                       AS time_index,
            ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
            ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS avg_ctr,
            ROUND(AVG(cam.cpc)::NUMERIC, 2)               AS avg_cpc,
            ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)   AS avg_conversion_rate,
            ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
            ROUND(AVG(cam.engagement_rate)::NUMERIC, 5)   AS avg_engagement_rate
        FROM campaigns cam
        JOIN calendar c ON cam.start_date = c.date
        WHERE 1=1
        {plat_filter}
        GROUP BY c.year, c.month
        ORDER BY c.year, c.month
    """)

    rows = db.execute(query, params).mappings().all()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Anomaly detection
# ─────────────────────────────────────────────────────────────
def detect_anomalies(
    db:              Session,
    platform:        Optional[str] = None,
    contamination:   float = 0.1,
    top_n_anomalies: int   = 5,
) -> dict:
    """
    Detect statistically anomalous months in KPI history.

    Args:
        db:              SQLAlchemy session
        platform:        Optional platform filter
        contamination:   Expected proportion of anomalies (0.1 = 10%)
        top_n_anomalies: Return this many worst anomalies

    Returns:
        Dict with anomaly list and formatted summary
    """
    logger.info(f"Running anomaly detection | platform={platform}")

    rows = _fetch_monthly_data(db=db, platform=platform)

    if len(rows) < 12:
        return {
            "status":    "insufficient_data",
            "anomalies": [],
            "formatted": "Need at least 12 months of data for anomaly detection.",
        }

    # Build feature matrix
    features = []
    for row in rows:
        features.append([
            float(row["avg_roi"]             or 0),
            float(row["avg_roas"]            or 0),
            float(row["avg_ctr"]             or 0),
            float(row["avg_cpc"]             or 0),
            float(row["avg_conversion_rate"] or 0),
            float(row["total_revenue"]       or 0),
            float(row["avg_engagement_rate"] or 0),
        ])

    X = np.array(features)

    # Scale features — important for Isolation Forest
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Isolation Forest
    model = IsolationForest(
        contamination=contamination,
        random_state=42,       # reproducible results
        n_estimators=100,
    )
    model.fit(X_scaled)

    # Get anomaly scores and predictions
    # scores: more negative = more anomalous
    # predictions: -1 = anomaly, 1 = normal
    scores      = model.score_samples(X_scaled)
    predictions = model.predict(X_scaled)

    # Collect anomalous months
    anomalies = []
    for i, (row, score, pred) in enumerate(zip(rows, scores, predictions)):
        if pred == -1:  # flagged as anomaly
            anomalies.append({
                "year":              int(row["year"]),
                "month":             int(row["month"]),
                "period":            f"{int(row['year'])}-{str(int(row['month'])).zfill(2)}",
                "anomaly_score":     round(float(score), 4),
                "avg_roi":           float(row["avg_roi"]             or 0),
                "avg_roas":          float(row["avg_roas"]            or 0),
                "avg_ctr":           float(row["avg_ctr"]             or 0),
                "avg_cpc":           float(row["avg_cpc"]             or 0),
                "avg_conversion_rate": float(row["avg_conversion_rate"] or 0),
                "total_revenue":     float(row["total_revenue"]       or 0),
                "avg_engagement_rate": float(row["avg_engagement_rate"] or 0),
            })

    # Sort by anomaly score — most anomalous first
    anomalies.sort(key=lambda x: x["anomaly_score"])
    top_anomalies = anomalies[:top_n_anomalies]

    # Calculate baseline stats for context
    roi_values = [float(r["avg_roi"] or 0) for r in rows]
    rev_values = [float(r["total_revenue"] or 0) for r in rows]

    baseline = {
        "avg_roi":     round(float(np.mean(roi_values)), 4),
        "std_roi":     round(float(np.std(roi_values)),  4),
        "avg_revenue": round(float(np.mean(rev_values)), 2),
        "std_revenue": round(float(np.std(rev_values)),  2),
        "total_months_analyzed": len(rows),
        "anomalous_months_found": len(anomalies),
    }

    platform_label = platform or "All Platforms"

    # Format for prompt injection
    lines = [
        f"ML ANOMALY DETECTION — {platform_label.upper()}:",
        f"  Months analyzed   : {baseline['total_months_analyzed']}",
        f"  Anomalies found   : {baseline['anomalous_months_found']}",
        f"  Baseline avg ROI  : {baseline['avg_roi']} (±{baseline['std_roi']})",
        f"  Baseline avg Rev  : ${baseline['avg_revenue']:,.2f} "
        f"(±${baseline['std_revenue']:,.2f})",
        "",
        f"TOP {len(top_anomalies)} MOST ANOMALOUS PERIODS:",
    ]

    for i, a in enumerate(top_anomalies, 1):
        roi_diff = a["avg_roi"] - baseline["avg_roi"]
        rev_diff = a["total_revenue"] - baseline["avg_revenue"]

        lines.append(
            f"\n  #{i} — {a['period']} "
            f"(anomaly score: {a['anomaly_score']})"
        )
        lines.append(
            f"      ROI      : {a['avg_roi']} "
            f"({'▼' if roi_diff < 0 else '▲'} "
            f"{abs(round(roi_diff, 4))} vs baseline)"
        )
        lines.append(
            f"      ROAS     : {a['avg_roas']}"
        )
        lines.append(
            f"      Revenue  : ${a['total_revenue']:,.2f} "
            f"({'▼' if rev_diff < 0 else '▲'} "
            f"${abs(round(rev_diff, 2)):,.2f} vs baseline)"
        )
        lines.append(
            f"      CTR      : {a['avg_ctr']} "
            f"| CPC: ${a['avg_cpc']} "
            f"| Conv.Rate: {a['avg_conversion_rate']}"
        )

    formatted = "\n".join(lines)

    return {
        "status":          "success",
        "platform":        platform_label,
        "baseline":        baseline,
        "anomalies":       anomalies,
        "top_anomalies":   top_anomalies,
        "formatted":       formatted,
    }