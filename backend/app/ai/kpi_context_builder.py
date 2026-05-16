"""
KPI Context Builder — Phase 3.

Queries real PostgreSQL data based on detected intent,
formats results into structured text, and returns it
for injection into the AI prompt.

Architecture principle:
- SQL fetches the facts
- This module formats them
- The LLM only explains them

Never let the LLM generate numbers.
Always inject real numbers into the prompt.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger("sma_api.kpi_context_builder")


# ─────────────────────────────────────────────────────────────
# Time period → SQL date filter builder
# Maps our intent_detector time codes to real SQL conditions
# ─────────────────────────────────────────────────────────────
def _build_date_filter(time_period: Optional[str]) -> tuple[str, dict]:
    """
    Convert time_period code into SQL WHERE clause + params.

    Returns:
        (sql_condition_string, params_dict)
    """
    filters = {
        "last_month": (
            """
            EXTRACT(YEAR  FROM cam.start_date) = EXTRACT(YEAR  FROM CURRENT_DATE - INTERVAL '1 month')
            AND EXTRACT(MONTH FROM cam.start_date) = EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')
            """,
            {}
        ),
        "this_month": (
            """
            EXTRACT(YEAR  FROM cam.start_date) = EXTRACT(YEAR  FROM CURRENT_DATE)
            AND EXTRACT(MONTH FROM cam.start_date) = EXTRACT(MONTH FROM CURRENT_DATE)
            """,
            {}
        ),
        "last_quarter": (
            """
            cam.start_date >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '3 months')
            AND cam.start_date <  DATE_TRUNC('quarter', CURRENT_DATE)
            """,
            {}
        ),
        "this_quarter": (
            """
            cam.start_date >= DATE_TRUNC('quarter', CURRENT_DATE)
            """,
            {}
        ),
        "last_year": (
            """
            EXTRACT(YEAR FROM cam.start_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1
            """,
            {}
        ),
        "this_year": (
            """
            EXTRACT(YEAR FROM cam.start_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            """,
            {}
        ),
        "last_week": (
            """
            cam.start_date >= DATE_TRUNC('week', CURRENT_DATE - INTERVAL '7 days')
            AND cam.start_date <  DATE_TRUNC('week', CURRENT_DATE)
            """,
            {}
        ),
    }

    if time_period and time_period in filters:
        condition, params = filters[time_period]
        return f"AND {condition}", params

    # No time filter — use all data
    return "", {}


# ─────────────────────────────────────────────────────────────
# Platform filter builder
# ─────────────────────────────────────────────────────────────
def _build_platform_filter(platform: Optional[str]) -> tuple[str, dict]:
    """Returns SQL platform filter and params dict."""
    if platform:
        return "AND cam.platform = :platform", {"platform": platform}
    return "", {}


# ─────────────────────────────────────────────────────────────
# REVENUE KPI FETCHER
# Used for: revenue, anomaly intents
# ─────────────────────────────────────────────────────────────
def fetch_revenue_kpis(
    db: Session,
    platform: Optional[str] = None,
    time_period: Optional[str] = None,
) -> str:
    """
    Fetch revenue and profitability KPIs.
    Returns formatted text block for prompt injection.
    """
    date_sql, date_params = _build_date_filter(time_period)
    plat_sql, plat_params = _build_platform_filter(platform)
    params = {**date_params, **plat_params}

    query = text(f"""
        SELECT
            cam.platform,
            COUNT(cam.campaign_id)                        AS total_campaigns,
            ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS total_ad_spend,
            ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
            ROUND(SUM(cam.profit_generated)::NUMERIC, 2)  AS total_profit,
            ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
            ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS avg_ctr,
            ROUND(AVG(cam.cpc)::NUMERIC, 2)               AS avg_cpc,
            ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)   AS avg_conversion_rate
        FROM campaigns cam
        WHERE 1=1
        {plat_sql}
        {date_sql}
        GROUP BY cam.platform
        ORDER BY total_revenue DESC
    """)

    try:
        rows = db.execute(query, params).mappings().all()
        if not rows:
            return "No revenue data found for the specified filters."

        lines = ["REVENUE & PROFITABILITY KPIs:"]
        for row in rows:
            lines.append(
                f"\nPlatform: {row['platform']}"
                f"\n  - Campaigns Run    : {row['total_campaigns']}"
                f"\n  - Total Ad Spend   : ${row['total_ad_spend']:,.2f}"
                f"\n  - Total Revenue    : ${row['total_revenue']:,.2f}"
                f"\n  - Total Profit     : ${row['total_profit']:,.2f}"
                f"\n  - Avg ROAS         : {row['avg_roas']}"
                f"\n  - Avg ROI          : {row['avg_roi']}"
                f"\n  - Avg CTR          : {row['avg_ctr']}"
                f"\n  - Avg CPC          : ${row['avg_cpc']}"
                f"\n  - Avg Conv. Rate   : {row['avg_conversion_rate']}"
            )
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Revenue KPI fetch error: {e}", exc_info=True)
        return "Revenue KPI data temporarily unavailable."


# ─────────────────────────────────────────────────────────────
# CAMPAIGN KPI FETCHER
# Used for: campaign intent
# ─────────────────────────────────────────────────────────────
def fetch_campaign_kpis(
    db: Session,
    platform: Optional[str] = None,
    time_period: Optional[str] = None,
) -> str:
    """
    Fetch campaign performance breakdown by type and objective.
    """
    date_sql, date_params = _build_date_filter(time_period)
    plat_sql, plat_params = _build_platform_filter(platform)
    params = {**date_params, **plat_params}

    # Campaign type performance
    type_query = text(f"""
        SELECT
            cam.platform,
            cam.campaign_type,
            COUNT(cam.campaign_id)                       AS total_campaigns,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)              AS avg_ctr,
            ROUND(AVG(cam.cpc)::NUMERIC, 2)              AS avg_cpc,
            ROUND(AVG(cam.roas)::NUMERIC, 4)             AS avg_roas,
            ROUND(AVG(cam.roi)::NUMERIC, 4)              AS avg_roi,
            ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate
        FROM campaigns cam
        WHERE 1=1
        {plat_sql}
        {date_sql}
        GROUP BY cam.platform, cam.campaign_type
        ORDER BY cam.platform, avg_roas DESC
    """)

    # Influencer impact
    influencer_query = text(f"""
        SELECT
            cam.influencer_used,
            COUNT(cam.campaign_id)                       AS total_campaigns,
            ROUND(AVG(cam.roas)::NUMERIC, 4)             AS avg_roas,
            ROUND(AVG(cam.roi)::NUMERIC, 4)              AS avg_roi,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)              AS avg_ctr,
            ROUND(AVG(cam.engagement_rate)::NUMERIC, 5)  AS avg_engagement_rate
        FROM campaigns cam
        WHERE 1=1
        {plat_sql}
        {date_sql}
        GROUP BY cam.influencer_used
    """)

    try:
        type_rows = db.execute(type_query, params).mappings().all()
        inf_rows  = db.execute(influencer_query, params).mappings().all()

        lines = ["CAMPAIGN PERFORMANCE KPIs:"]

        if type_rows:
            lines.append("\nBy Campaign Type:")
            for row in type_rows:
                lines.append(
                    f"  [{row['platform']}] {row['campaign_type']}"
                    f" → ROAS: {row['avg_roas']} | ROI: {row['avg_roi']}"
                    f" | CTR: {row['avg_ctr']} | CPC: ${row['avg_cpc']}"
                    f" | Conv.Rate: {row['avg_conversion_rate']}"
                    f" | Campaigns: {row['total_campaigns']}"
                )

        if inf_rows:
            lines.append("\nInfluencer Impact:")
            for row in inf_rows:
                label = "With Influencer" if row["influencer_used"] else "Without Influencer"
                lines.append(
                    f"  {label}"
                    f" → ROAS: {row['avg_roas']} | ROI: {row['avg_roi']}"
                    f" | CTR: {row['avg_ctr']}"
                    f" | Engagement: {row['avg_engagement_rate']}"
                    f" | Campaigns: {row['total_campaigns']}"
                )

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Campaign KPI fetch error: {e}", exc_info=True)
        return "Campaign KPI data temporarily unavailable."


# ─────────────────────────────────────────────────────────────
# AUDIENCE KPI FETCHER
# Used for: audience intent
# ─────────────────────────────────────────────────────────────
def fetch_audience_kpis(
    db: Session,
    platform: Optional[str] = None,
    time_period: Optional[str] = None,
) -> str:
    """
    Fetch audience demographics and conversion performance.
    """
    date_sql, date_params = _build_date_filter(time_period)
    plat_sql, plat_params = _build_platform_filter(platform)
    params = {**date_params, **plat_params}

    age_query = text(f"""
        SELECT
            cam.audience_age_group,
            COUNT(cam.campaign_id)                       AS total_campaigns,
            SUM(cam.conversions)                         AS total_conversions,
            ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)              AS avg_ctr,
            ROUND(AVG(cam.roas)::NUMERIC, 4)             AS avg_roas
        FROM campaigns cam
        WHERE 1=1
        {plat_sql}
        {date_sql}
        GROUP BY cam.audience_age_group
        ORDER BY avg_conversion_rate DESC
    """)

    device_query = text(f"""
        SELECT
            cam.device_type,
            COUNT(cam.campaign_id)                       AS total_campaigns,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)              AS avg_ctr,
            ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
            ROUND(AVG(cam.roas)::NUMERIC, 4)             AS avg_roas
        FROM campaigns cam
        WHERE 1=1
        {plat_sql}
        {date_sql}
        GROUP BY cam.device_type
        ORDER BY avg_conversion_rate DESC
    """)

    try:
        age_rows    = db.execute(age_query, params).mappings().all()
        device_rows = db.execute(device_query, params).mappings().all()

        lines = ["AUDIENCE KPIs:"]

        if age_rows:
            lines.append("\nBy Age Group:")
            for row in age_rows:
                lines.append(
                    f"  Age {row['audience_age_group']}"
                    f" → Conv.Rate: {row['avg_conversion_rate']}"
                    f" | CTR: {row['avg_ctr']}"
                    f" | ROAS: {row['avg_roas']}"
                    f" | Total Conversions: {row['total_conversions']}"
                )

        if device_rows:
            lines.append("\nBy Device Type:")
            for row in device_rows:
                lines.append(
                    f"  {row['device_type']}"
                    f" → Conv.Rate: {row['avg_conversion_rate']}"
                    f" | CTR: {row['avg_ctr']}"
                    f" | ROAS: {row['avg_roas']}"
                )

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Audience KPI fetch error: {e}", exc_info=True)
        return "Audience KPI data temporarily unavailable."


# ─────────────────────────────────────────────────────────────
# PLATFORM KPI FETCHER
# Used for: platform intent
# ─────────────────────────────────────────────────────────────
def fetch_platform_kpis(
    db: Session,
    platform: Optional[str] = None,
    time_period: Optional[str] = None,
) -> str:
    """
    Fetch platform comparison KPIs including market benchmarks.
    """
    date_sql, date_params = _build_date_filter(time_period)
    plat_sql, plat_params = _build_platform_filter(platform)
    params = {**date_params, **plat_params}

    query = text(f"""
        SELECT
            cam.platform,
            p.avg_market_ctr                              AS market_benchmark_ctr,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS our_avg_ctr,
            ROUND(
                (AVG(cam.ctr) - p.avg_market_ctr)
                / NULLIF(p.avg_market_ctr, 0) * 100
            ::NUMERIC, 2)                                 AS ctr_vs_benchmark_pct,
            p.avg_market_cpc                              AS market_benchmark_cpc,
            ROUND(AVG(cam.cpc)::NUMERIC, 2)               AS our_avg_cpc,
            ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
            ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
            ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS total_spend,
            ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
            COUNT(cam.campaign_id)                        AS total_campaigns
        FROM campaigns cam
        JOIN platforms p ON cam.platform = p.platform_name
        WHERE 1=1
        {plat_sql}
        {date_sql}
        GROUP BY cam.platform, p.avg_market_ctr, p.avg_market_cpc
        ORDER BY avg_roas DESC
    """)

    try:
        rows = db.execute(query, params).mappings().all()
        if not rows:
            return "No platform data found for the specified filters."

        lines = ["PLATFORM BENCHMARK KPIs:"]
        for row in rows:
            direction = "above" if float(row["ctr_vs_benchmark_pct"] or 0) >= 0 else "below"
            lines.append(
                f"\nPlatform: {row['platform']}"
                f"\n  - Our CTR          : {row['our_avg_ctr']}"
                f"  (market: {row['market_benchmark_ctr']}"
                f" → {abs(float(row['ctr_vs_benchmark_pct'] or 0))}% {direction} benchmark)"
                f"\n  - Our CPC          : ${row['our_avg_cpc']}"
                f"  (market: ${row['market_benchmark_cpc']})"
                f"\n  - Avg ROAS         : {row['avg_roas']}"
                f"\n  - Avg ROI          : {row['avg_roi']}"
                f"\n  - Total Spend      : ${row['total_spend']:,.2f}"
                f"\n  - Total Revenue    : ${row['total_revenue']:,.2f}"
                f"\n  - Total Campaigns  : {row['total_campaigns']}"
            )
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Platform KPI fetch error: {e}", exc_info=True)
        return "Platform KPI data temporarily unavailable."


# ─────────────────────────────────────────────────────────────
# ENGAGEMENT KPI FETCHER
# Used for: engagement intent
# ─────────────────────────────────────────────────────────────
def fetch_engagement_kpis(
    db: Session,
    platform: Optional[str] = None,
    time_period: Optional[str] = None,
) -> str:
    """
    Fetch engagement and sentiment KPIs.
    """
    date_sql, date_params = _build_date_filter(time_period)
    plat_sql, plat_params = _build_platform_filter(platform)
    params = {**date_params, **plat_params}

    query = text(f"""
        SELECT
            cam.platform,
            COUNT(cam.campaign_id)                        AS total_campaigns,
            ROUND(AVG(cam.engagement_rate)::NUMERIC, 5)   AS avg_engagement_rate,
            ROUND(AVG(cam.sentiment_score)::NUMERIC, 3)   AS avg_sentiment_score,
            SUM(cam.likes)                                AS total_likes,
            SUM(cam.comments)                             AS total_comments,
            SUM(cam.shares)                               AS total_shares,
            SUM(cam.saves)                                AS total_saves,
            SUM(cam.impressions)                          AS total_impressions,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS avg_ctr
        FROM campaigns cam
        WHERE 1=1
        {plat_sql}
        {date_sql}
        GROUP BY cam.platform
        ORDER BY avg_engagement_rate DESC
    """)

    try:
        rows = db.execute(query, params).mappings().all()
        if not rows:
            return "No engagement data found for the specified filters."

        lines = ["ENGAGEMENT & SENTIMENT KPIs:"]
        for row in rows:
            sentiment = float(row["avg_sentiment_score"] or 0)
            sentiment_label = (
                "Positive" if sentiment > 0.2
                else "Negative" if sentiment < -0.2
                else "Neutral"
            )
            lines.append(
                f"\nPlatform: {row['platform']}"
                f"\n  - Engagement Rate  : {row['avg_engagement_rate']}"
                f"\n  - Sentiment Score  : {row['avg_sentiment_score']}"
                f" ({sentiment_label})"
                f"\n  - Total Likes      : {row['total_likes']:,}"
                f"\n  - Total Comments   : {row['total_comments']:,}"
                f"\n  - Total Shares     : {row['total_shares']:,}"
                f"\n  - Total Saves      : {row['total_saves']:,}"
                f"\n  - Total Impressions: {row['total_impressions']:,}"
                f"\n  - Avg CTR          : {row['avg_ctr']}"
            )
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Engagement KPI fetch error: {e}", exc_info=True)
        return "Engagement KPI data temporarily unavailable."


# ─────────────────────────────────────────────────────────────
# ANOMALY KPI FETCHER
# Used for: anomaly intent
# Fetches current period vs previous period for comparison
# ─────────────────────────────────────────────────────────────
def fetch_anomaly_kpis(
    db: Session,
    platform: Optional[str] = None,
    time_period: Optional[str] = None,
) -> str:
    """
    Fetch current period KPIs AND previous period KPIs.

    IMPORTANT: Uses the latest month available IN THE DATA,
    not CURRENT_DATE. This makes the system work correctly
    regardless of when it is run relative to data freshness.
    """
    plat_filter = "AND cam.platform = :platform" if platform else ""
    params      = {"platform": platform} if platform else {}

    # Step 1: Find the latest month that actually exists in the data
    latest_query = text(f"""
    SELECT
        EXTRACT(YEAR  FROM MAX(start_date))::INT AS latest_year,
        EXTRACT(MONTH FROM MAX(start_date))::INT AS latest_month
    FROM campaigns
    WHERE 1=1
    {'AND platform = :platform' if platform else ''}
""")

    try:
        latest_row = db.execute(latest_query, params).mappings().first()

        if not latest_row or not latest_row["latest_year"]:
            return "No campaign data found in the database."

        latest_year  = latest_row["latest_year"]
        latest_month = latest_row["latest_month"]

        # Step 2: Calculate previous month correctly
        # Handle January edge case → previous month = December of prior year
        if latest_month == 1:
            prev_year  = latest_year - 1
            prev_month = 12
        else:
            prev_year  = latest_year
            prev_month = latest_month - 1

        logger.info(
            f"Anomaly comparison: "
            f"current={latest_year}/{latest_month} "
            f"vs previous={prev_year}/{prev_month}"
        )

        # Step 3: Fetch current period (latest month in data)
        current_query = text(f"""
            SELECT
                cam.platform,
                COUNT(cam.campaign_id)                        AS total_campaigns,
                ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
                ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
                ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS avg_ctr,
                ROUND(AVG(cam.cpc)::NUMERIC, 2)               AS avg_cpc,
                ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)   AS avg_conversion_rate,
                ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS total_ad_spend,
                ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
                ROUND(AVG(cam.engagement_rate)::NUMERIC, 5)   AS avg_engagement_rate,
                ROUND(AVG(cam.sentiment_score)::NUMERIC, 3)   AS avg_sentiment
            FROM campaigns cam
            WHERE EXTRACT(YEAR  FROM cam.start_date) = :curr_year
              AND EXTRACT(MONTH FROM cam.start_date) = :curr_month
            {plat_filter}
            GROUP BY cam.platform
        """)

        # Step 4: Fetch previous period
        previous_query = text(f"""
            SELECT
                cam.platform,
                ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
                ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
                ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS avg_ctr,
                ROUND(AVG(cam.cpc)::NUMERIC, 2)               AS avg_cpc,
                ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)   AS avg_conversion_rate,
                ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS total_ad_spend,
                ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue
            FROM campaigns cam
            WHERE EXTRACT(YEAR  FROM cam.start_date) = :prev_year
              AND EXTRACT(MONTH FROM cam.start_date) = :prev_month
            {plat_filter}
            GROUP BY cam.platform
        """)

        curr_params = {
            **params,
            "curr_year": latest_year,
            "curr_month": latest_month,
        }
        prev_params = {
            **params,
            "prev_year": prev_year,
            "prev_month": prev_month,
        }

        curr_rows = db.execute(current_query,  curr_params).mappings().all()
        prev_rows = db.execute(previous_query, prev_params).mappings().all()

        prev_by_platform = {r["platform"]: r for r in prev_rows}

        lines = [
            f"ANOMALY ANALYSIS — PERIOD COMPARISON:",
            f"Current Period : {latest_year}-{str(latest_month).zfill(2)}",
            f"Previous Period: {prev_year}-{str(prev_month).zfill(2)}",
        ]

        if not curr_rows:
            lines.append("No data found for the current period.")
            return "\n".join(lines)

        for curr in curr_rows:
            plat = curr["platform"]
            prev = prev_by_platform.get(plat)

            lines.append(f"\nPlatform: {plat}")
            lines.append(f"  CURRENT ({latest_year}-{str(latest_month).zfill(2)}):")
            lines.append(f"    ROI: {curr['avg_roi']} | ROAS: {curr['avg_roas']}")
            lines.append(f"    CTR: {curr['avg_ctr']} | CPC: ${curr['avg_cpc']}")
            lines.append(f"    Conv.Rate : {curr['avg_conversion_rate']}")
            lines.append(f"    Ad Spend  : ${curr['total_ad_spend']:,.2f}")
            lines.append(f"    Revenue   : ${curr['total_revenue']:,.2f}")
            lines.append(f"    Engagement: {curr['avg_engagement_rate']}")
            lines.append(f"    Sentiment : {curr['avg_sentiment']}")

            if prev:
                lines.append(f"  PREVIOUS ({prev_year}-{str(prev_month).zfill(2)}):")
                lines.append(f"    ROI: {prev['avg_roi']} | ROAS: {prev['avg_roas']}")
                lines.append(f"    CTR: {prev['avg_ctr']} | CPC: ${prev['avg_cpc']}")
                lines.append(f"    Conv.Rate: {prev['avg_conversion_rate']}")
                lines.append(
                    f"    Ad Spend : ${prev['total_ad_spend']:,.2f}"
                    f" | Revenue: ${prev['total_revenue']:,.2f}"
                )

                def _delta(curr_val, prev_val):
                    try:
                        c, p = float(curr_val or 0), float(prev_val or 0)
                        if p == 0:
                            return "N/A"
                        change    = ((c - p) / p) * 100
                        direction = "▲" if change >= 0 else "▼"
                        return f"{direction} {abs(round(change, 2))}%"
                    except Exception:
                        return "N/A"

                lines.append("  CHANGES:")
                lines.append(f"    ROI       : {_delta(curr['avg_roi'],             prev['avg_roi'])}")
                lines.append(f"    ROAS      : {_delta(curr['avg_roas'],            prev['avg_roas'])}")
                lines.append(f"    CTR       : {_delta(curr['avg_ctr'],             prev['avg_ctr'])}")
                lines.append(f"    CPC       : {_delta(curr['avg_cpc'],             prev['avg_cpc'])}")
                lines.append(f"    Conv.Rate : {_delta(curr['avg_conversion_rate'], prev['avg_conversion_rate'])}")
                lines.append(f"    Revenue   : {_delta(curr['total_revenue'],       prev['total_revenue'])}")
            else:
                lines.append("  PREVIOUS PERIOD: No comparison data available.")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Anomaly KPI fetch error: {e}", exc_info=True)
        return "Anomaly KPI data temporarily unavailable."


# ─────────────────────────────────────────────────────────────
# MASTER DISPATCHER
# Called by orchestrator — routes to correct fetcher
# ─────────────────────────────────────────────────────────────
def build_kpi_context(
    intent: str,
    db: Session,
    platform: Optional[str] = None,
    time_period: Optional[str] = None,
) -> str:
    """
    Master function called by the orchestrator.
    Routes to the correct KPI fetcher based on intent.

    Args:
        intent:      Detected intent category
        db:          SQLAlchemy session
        platform:    Detected platform (optional)
        time_period: Detected time period (optional)

    Returns:
        Formatted KPI text block for prompt injection
    """
    logger.info(
        f"Building KPI context | intent={intent} "
        f"| platform={platform} | time={time_period}"
    )

    fetchers = {
        "revenue":    fetch_revenue_kpis,
        "anomaly":    fetch_anomaly_kpis,
        "campaign":   fetch_campaign_kpis,
        "audience":   fetch_audience_kpis,
        "platform":   fetch_platform_kpis,
        "engagement": fetch_engagement_kpis,
    }

    fetcher = fetchers.get(intent)

    if fetcher is None:
        logger.info(f"No KPI fetcher for intent '{intent}' — returning empty context")
        return ""

    return fetcher(db=db, platform=platform, time_period=time_period)