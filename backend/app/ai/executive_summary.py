"""
Executive Summary Engine — Phase 5.

Generates a board-ready AI summary across ALL platforms.

Flow:
1. Fetch KPIs for all platforms (latest month vs previous)
2. Run recommendation engine across all platforms
3. Run alert scanner
4. Send everything to LLM for synthesis
5. Return structured executive report
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.ai.chat_service import get_ai_response
from app.ai.smart_alerts import scan_all_alerts

logger = logging.getLogger("sma_api.executive_summary")


# ─────────────────────────────────────────────────────────────
# Data fetcher — comprehensive all-platform summary
# ─────────────────────────────────────────────────────────────
def _fetch_executive_data(db: Session) -> tuple[str, str]:
    """
    Fetch comprehensive cross-platform KPI data
    for the executive summary prompt.
    Returns (formatted_data_string, period_label).
    """

    # Overall platform summary
    platform_query = text("""
        WITH latest AS (
            SELECT
                EXTRACT(YEAR  FROM MAX(start_date))::INT AS yr,
                EXTRACT(MONTH FROM MAX(start_date))::INT AS mo
            FROM campaigns
        ),
        current_period AS (
            SELECT
                cam.platform,
                COUNT(cam.campaign_id)                        AS total_campaigns,
                ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
                ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
                ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS avg_ctr,
                ROUND(AVG(cam.cpc)::NUMERIC, 2)               AS avg_cpc,
                ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)   AS avg_conversion_rate,
                ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
                ROUND(SUM(cam.profit_generated)::NUMERIC, 2)  AS total_profit,
                ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS total_ad_spend,
                ROUND(AVG(cam.engagement_rate)::NUMERIC, 5)   AS avg_engagement_rate,
                ROUND(AVG(cam.sentiment_score)::NUMERIC, 3)   AS avg_sentiment,
                latest.yr                                     AS data_year,
                latest.mo                                     AS data_month
            FROM campaigns cam
            CROSS JOIN latest
            WHERE EXTRACT(YEAR  FROM cam.start_date) = latest.yr
              AND EXTRACT(MONTH FROM cam.start_date) = latest.mo
            GROUP BY cam.platform, latest.yr, latest.mo
        ),
        previous_period AS (
            SELECT
                cam.platform,
                ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
                ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
                ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue
            FROM campaigns cam
            CROSS JOIN latest
            WHERE (
                CASE
                    WHEN latest.mo = 1
                    THEN EXTRACT(YEAR  FROM cam.start_date) = latest.yr - 1
                         AND EXTRACT(MONTH FROM cam.start_date) = 12
                    ELSE EXTRACT(YEAR  FROM cam.start_date) = latest.yr
                         AND EXTRACT(MONTH FROM cam.start_date) = latest.mo - 1
                END
            )
            GROUP BY cam.platform
        )
        SELECT
            c.*,
            p.avg_roi        AS prev_roi,
            p.avg_roas       AS prev_roas,
            p.total_revenue  AS prev_revenue,
            ROUND(
                (c.total_revenue - p.total_revenue)
                * 100.0 / NULLIF(p.total_revenue, 0)
            ::NUMERIC, 2)    AS revenue_change_pct,
            ROUND(
                (c.avg_roi - p.avg_roi)
                * 100.0 / NULLIF(p.avg_roi, 0)
            ::NUMERIC, 2)    AS roi_change_pct
        FROM current_period  c
        LEFT JOIN previous_period p ON c.platform = p.platform
        ORDER BY c.total_revenue DESC
    """)

    # Overall business totals
    totals_query = text("""
        WITH latest AS (
            SELECT
                EXTRACT(YEAR  FROM MAX(start_date))::INT AS yr,
                EXTRACT(MONTH FROM MAX(start_date))::INT AS mo
            FROM campaigns
        )
        SELECT
            latest.yr                                     AS data_year,
            latest.mo                                     AS data_month,
            COUNT(cam.campaign_id)                        AS total_campaigns,
            ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
            ROUND(SUM(cam.profit_generated)::NUMERIC, 2)  AS total_profit,
            ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS total_ad_spend,
            ROUND(AVG(cam.roas)::NUMERIC, 4)              AS overall_roas,
            ROUND(AVG(cam.roi)::NUMERIC, 4)               AS overall_roi,
            SUM(cam.conversions)                          AS total_conversions,
            ROUND(AVG(cam.sentiment_score)::NUMERIC, 3)   AS avg_sentiment
        FROM campaigns cam
        CROSS JOIN latest
        WHERE EXTRACT(YEAR  FROM cam.start_date) = latest.yr
          AND EXTRACT(MONTH FROM cam.start_date) = latest.mo
        GROUP BY latest.yr, latest.mo
    """)

    try:
        plat_rows   = db.execute(platform_query).mappings().all()
        totals_row  = db.execute(totals_query).mappings().first()

        if not plat_rows or not totals_row:
            return "No data available.", ""

        year  = totals_row["data_year"]
        month = totals_row["data_month"]
        period = f"{year}-{str(month).zfill(2)}"

        lines = [
            f"EXECUTIVE SUMMARY DATA — Period: {period}",
            "",
            "OVERALL BUSINESS PERFORMANCE:",
            f"  Total Revenue    : ${totals_row['total_revenue']:,.2f}",
            f"  Total Profit     : ${totals_row['total_profit']:,.2f}",
            f"  Total Ad Spend   : ${totals_row['total_ad_spend']:,.2f}",
            f"  Overall ROAS     : {totals_row['overall_roas']}",
            f"  Overall ROI      : {totals_row['overall_roi']}",
            f"  Total Conversions: {totals_row['total_conversions']:,}",
            f"  Total Campaigns  : {totals_row['total_campaigns']}",
            f"  Avg Sentiment    : {totals_row['avg_sentiment']}",
            "",
            "PLATFORM BREAKDOWN:",
        ]

        for row in plat_rows:
            rev_change = row["revenue_change_pct"]
            roi_change = row["roi_change_pct"]

            rev_arrow = "▲" if rev_change and rev_change >= 0 else "▼"
            roi_arrow = "▲" if roi_change and roi_change >= 0 else "▼"

            lines.append(f"\n  {row['platform'].upper()}:")
            lines.append(
                f"    Revenue      : ${row['total_revenue']:,.2f}"
                f" ({rev_arrow} {abs(float(rev_change or 0)):.1f}% vs prev month)"
            )
            lines.append(
                f"    Profit       : ${row['total_profit']:,.2f}"
            )
            lines.append(
                f"    Ad Spend     : ${row['total_ad_spend']:,.2f}"
            )
            lines.append(
                f"    ROAS         : {row['avg_roas']}"
                f" ({roi_arrow} {abs(float(roi_change or 0)):.1f}% ROI change)"
            )
            lines.append(f"    CTR          : {row['avg_ctr']}")
            lines.append(f"    Conv. Rate   : {row['avg_conversion_rate']}")
            lines.append(f"    Engagement   : {row['avg_engagement_rate']}")
            lines.append(f"    Sentiment    : {row['avg_sentiment']}")
            lines.append(f"    Campaigns    : {row['total_campaigns']}")

        return "\n".join(lines), period

    except Exception as e:
        logger.error(f"Executive data fetch error: {e}", exc_info=True)
        return "Executive data temporarily unavailable.", ""


# ─────────────────────────────────────────────────────────────
# Executive summary generator
# ─────────────────────────────────────────────────────────────
def generate_executive_summary(db: Session) -> dict:
    """
    Generate a complete AI-powered executive summary.

    1. Fetch cross-platform KPI data
    2. Scan alerts
    3. Send to LLM for executive synthesis
    4. Return structured report
    """
    logger.info("Generating executive summary...")

    # Fetch data
    exec_data, period = _fetch_executive_data(db)

    # Run alert scanner
    alert_report = scan_all_alerts(db)
    alert_summary = (
        f"{alert_report.critical_count} critical alerts, "
        f"{alert_report.warning_count} warnings across "
        f"{alert_report.platforms_scanned} platforms."
    )

    # Format top alerts for the prompt
    top_alerts = alert_report.alerts[:8]  # Top 8 most important
    alert_lines = []
    for a in sorted(top_alerts, key=lambda x: 0 if x.severity == "CRITICAL" else 1):
        alert_lines.append(
            f"  [{a.severity}] {a.platform} — {a.metric}: {a.message}"
        )

    alert_text = "\n".join(alert_lines) if alert_lines else "No critical alerts."

    # Build executive prompt
    prompt = f"""
You are preparing a monthly executive briefing for senior leadership.
Write a professional, structured executive summary in clear business language.

The summary must include these sections:
1. PERFORMANCE OVERVIEW — overall business health this month
2. PLATFORM HIGHLIGHTS — top performer and underperformer with reasons
3. KEY ALERTS — critical issues requiring immediate attention
4. STRATEGIC RECOMMENDATIONS — top 3 actions for next month
5. OUTLOOK — brief forward-looking statement

Tone: Professional, direct, data-driven. Like a McKinsey briefing.
Format: Use clear headers. Be concise. Executives want facts, not fluff.

---

{exec_data}

---

ALERT SUMMARY: {alert_summary}

TOP ALERTS:
{alert_text}

---

IMPORTANT:
- Use exact numbers from the data provided
- Do not fabricate any metrics
- Keep the entire summary under 500 words
- Make recommendations specific and actionable
- Identify the best and worst performing platform by name
"""

    result = get_ai_response(prompt)

    return {
        "period":           period,
        "summary":          result["answer"],
        "model":            result["model"],
        "tokens_used":      result["tokens_used"],
        "alert_summary":    alert_summary,
        "critical_alerts":  alert_report.critical_count,
        "warning_alerts":   alert_report.warning_count,
        "platforms_scanned": alert_report.platforms_scanned,
    }