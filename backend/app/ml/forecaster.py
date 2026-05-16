"""
KPI Forecaster — Phase 8.

Uses Linear Regression to forecast next month's KPI values
based on historical monthly trends from your PostgreSQL data.

Why Linear Regression:
- Interpretable — you can explain the prediction
- Works well with 6 years of monthly data (72 data points)
- Fast — trains in milliseconds
- Handles trends and seasonality via feature engineering

Models are trained fresh per request — no stale cached models.
For production at scale, add model caching with joblib.
"""

import logging
import numpy as np
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("sma_api.forecaster")


# ─────────────────────────────────────────────────────────────
# Data fetcher — monthly KPI history
# ─────────────────────────────────────────────────────────────
def _fetch_monthly_kpis(
    db: Session,
    platform: Optional[str] = None,
) -> list[dict]:
    """
    Fetch monthly aggregated KPIs for model training.
    Returns chronologically ordered list of monthly data points.
    """
    plat_filter = "AND cam.platform = :platform" if platform else ""
    params      = {"platform": platform} if platform else {}

    query = text(f"""
        SELECT
            c.year,
            c.month,
            (c.year * 12 + c.month)                        AS time_index,
            ROUND(AVG(cam.roi)::NUMERIC, 4)                AS avg_roi,
            ROUND(AVG(cam.roas)::NUMERIC, 4)               AS avg_roas,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)                AS avg_ctr,
            ROUND(AVG(cam.cpc)::NUMERIC, 2)                AS avg_cpc,
            ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)    AS avg_conversion_rate,
            ROUND(SUM(cam.revenue_generated)::NUMERIC, 2)  AS total_revenue,
            ROUND(AVG(cam.engagement_rate)::NUMERIC, 5)    AS avg_engagement_rate,
            COUNT(cam.campaign_id)                         AS total_campaigns
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
# Feature engineering
# We add month as a cyclical feature to capture seasonality
# sin/cos encoding preserves the circular nature of months
# (December is close to January, not far away)
# ─────────────────────────────────────────────────────────────
def _build_features(rows: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """
    Build feature matrix X and time index array.

    Features per data point:
    - time_index      : linear time progression
    - month_sin       : sine encoding of month (seasonality)
    - month_cos       : cosine encoding of month (seasonality)
    - total_campaigns : volume signal
    """
    X = []
    t = []

    for row in rows:
        month      = int(row["month"])
        time_idx   = int(row["time_index"])
        month_sin  = np.sin(2 * np.pi * month / 12)
        month_cos  = np.cos(2 * np.pi * month / 12)
        campaigns  = int(row["total_campaigns"])

        X.append([time_idx, month_sin, month_cos, campaigns])
        t.append(time_idx)

    return np.array(X), np.array(t)


def _get_next_month(rows: list[dict]) -> tuple[int, int, int]:
    """
    Calculate the year, month, and time_index for the next prediction.
    """
    last       = rows[-1]
    last_year  = int(last["year"])
    last_month = int(last["month"])

    if last_month == 12:
        next_year  = last_year + 1
        next_month = 1
    else:
        next_year  = last_year
        next_month = last_month + 1

    next_time_index = next_year * 12 + next_month
    return next_year, next_month, next_time_index


# ─────────────────────────────────────────────────────────────
# Single KPI forecaster
# ─────────────────────────────────────────────────────────────
def _forecast_kpi(
    rows:    list[dict],
    kpi_key: str,
    X:       np.ndarray,
) -> dict:
    """
    Train a linear regression model for one KPI and predict next month.

    Returns:
        dict with prediction, trend direction, confidence
    """
    try:
        # Extract target values
        y = np.array([float(row[kpi_key] or 0) for row in rows])

        # Need at least 6 months of data to fit meaningfully
        if len(y) < 6:
            return {"error": "insufficient_data", "kpi": kpi_key}

        # Scale features for better numerical stability
        scaler  = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train model
        model = LinearRegression()
        model.fit(X_scaled, y)

        # Score the model
        r2_score = model.score(X_scaled, y)

        # Build next month features
        next_year, next_month, next_time_idx = _get_next_month(rows)
        next_month_sin = np.sin(2 * np.pi * next_month / 12)
        next_month_cos = np.cos(2 * np.pi * next_month / 12)
        avg_campaigns  = float(np.mean([r["total_campaigns"] for r in rows]))

        next_X = np.array([[
            next_time_idx,
            next_month_sin,
            next_month_cos,
            avg_campaigns,
        ]])
        next_X_scaled = scaler.transform(next_X)

        # Predict
        prediction = float(model.predict(next_X_scaled)[0])

        # Calculate trend from last 3 months
        recent_values = y[-3:]
        if len(recent_values) >= 2:
            trend_pct = (
                (recent_values[-1] - recent_values[0])
                / abs(recent_values[0]) * 100
                if recent_values[0] != 0 else 0
            )
        else:
            trend_pct = 0

        trend_direction = (
            "improving" if trend_pct > 2
            else "declining" if trend_pct < -2
            else "stable"
        )

        # Confidence based on R² score
        confidence = (
            "high"   if r2_score > 0.7
            else "medium" if r2_score > 0.4
            else "low"
        )

        return {
            "kpi":              kpi_key,
            "predicted_value":  round(prediction, 4),
            "current_value":    round(float(y[-1]), 4),
            "trend_direction":  trend_direction,
            "trend_pct_3m":    round(trend_pct, 2),
            "r2_score":        round(r2_score, 4),
            "confidence":      confidence,
            "next_year":       next_year,
            "next_month":      next_month,
        }

    except Exception as e:
        logger.error(f"Forecast error for {kpi_key}: {e}")
        return {"error": str(e), "kpi": kpi_key}


# ─────────────────────────────────────────────────────────────
# Master forecasting function
# ─────────────────────────────────────────────────────────────
def generate_forecasts(
    db:       Session,
    platform: Optional[str] = None,
) -> dict:
    """
    Generate next-month forecasts for all key KPIs.

    Args:
        db:       SQLAlchemy session
        platform: Optional platform filter

    Returns:
        Dict with forecasts per KPI and formatted summary text
    """
    logger.info(f"Generating forecasts | platform={platform}")

    rows = _fetch_monthly_kpis(db=db, platform=platform)

    if len(rows) < 6:
        return {
            "status":    "insufficient_data",
            "message":   "Need at least 6 months of data for forecasting",
            "forecasts": {},
            "formatted": "Insufficient data for ML forecasting.",
        }

    X, _ = _build_features(rows)

    # KPIs to forecast
    kpis_to_forecast = [
        "avg_roi",
        "avg_roas",
        "avg_ctr",
        "avg_cpc",
        "avg_conversion_rate",
        "total_revenue",
        "avg_engagement_rate",
    ]

    forecasts = {}
    for kpi in kpis_to_forecast:
        forecasts[kpi] = _forecast_kpi(rows=rows, kpi_key=kpi, X=X)

    # Get period info
    next_year, next_month, _ = _get_next_month(rows)
    platform_label = platform or "All Platforms"

    # Format for prompt injection
    lines = [
        f"ML FORECASTS FOR {platform_label.upper()} "
        f"— Predicted: {next_year}-{str(next_month).zfill(2)}",
    ]

    kpi_labels = {
        "avg_roi":             ("ROI",             ""),
        "avg_roas":            ("ROAS",            "x"),
        "avg_ctr":             ("CTR",             ""),
        "avg_cpc":             ("CPC",             "$"),
        "avg_conversion_rate": ("Conversion Rate", ""),
        "total_revenue":       ("Revenue",         "$"),
        "avg_engagement_rate": ("Engagement Rate", ""),
    }

    for kpi, result in forecasts.items():
        if "error" in result:
            continue

        label, prefix = kpi_labels.get(kpi, (kpi, ""))
        current   = result["current_value"]
        predicted = result["predicted_value"]
        trend     = result["trend_direction"]
        conf      = result["confidence"]
        trend_3m  = result["trend_pct_3m"]

        direction = "▲" if predicted > current else "▼"
        change    = abs(((predicted - current) / current * 100)
                        if current != 0 else 0)

        lines.append(
            f"  {label}: {prefix}{current} → {prefix}{predicted} "
            f"({direction} {round(change, 1)}% predicted change) "
            f"| Trend: {trend} ({trend_3m:+.1f}% last 3 months) "
            f"| Confidence: {conf}"
        )

    formatted = "\n".join(lines)

    return {
        "status":      "success",
        "platform":    platform_label,
        "next_period": f"{next_year}-{str(next_month).zfill(2)}",
        "forecasts":   forecasts,
        "formatted":   formatted,
    }