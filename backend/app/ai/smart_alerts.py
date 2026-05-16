"""
Smart Alerts Engine — Phase 5.

Scans ALL platforms simultaneously.
Applies rule engine thresholds.
Returns structured alert list — NO LLM involved.

Design principles:
- Pure deterministic output
- Zero LLM token cost
- Fast enough to poll every 5 minutes
- Severity-sorted output
- Each alert is self-contained and actionable
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.ai.recommendation_engine import (
    THRESHOLDS,
    _f,
    _pct_change,
)

logger = logging.getLogger("sma_api.smart_alerts")


# ─────────────────────────────────────────────────────────────
# Alert data structure
# ─────────────────────────────────────────────────────────────
@dataclass
class Alert:
    severity:   str    # CRITICAL | WARNING
    platform:   str
    metric:     str
    current_value: str
    threshold:  str
    message:    str
    action:     str


@dataclass
class AlertReport:
    alerts:         list[Alert] = field(default_factory=list)
    critical_count: int = 0
    warning_count:  int = 0
    platforms_scanned: int = 0
    data_period:    str = ""

    def to_dict(self) -> dict:
        return {
            "critical_count":    self.critical_count,
            "warning_count":     self.warning_count,
            "platforms_scanned": self.platforms_scanned,
            "data_period":       self.data_period,
            "total_alerts":      len(self.alerts),
            "alerts": [
                {
                    "severity":      a.severity,
                    "platform":      a.platform,
                    "metric":        a.metric,
                    "current_value": a.current_value,
                    "threshold":     a.threshold,
                    "message":       a.message,
                    "action":        a.action,
                }
                for a in sorted(
                    self.alerts,
                    key=lambda x: 0 if x.severity == "CRITICAL" else 1,
                )
            ],
        }


# ─────────────────────────────────────────────────────────────
# Data fetcher — all platforms latest month
# ─────────────────────────────────────────────────────────────
def _fetch_all_platform_metrics(db: Session) -> tuple[list[dict], str]:
    """
    Fetch KPIs for ALL platforms for the latest data month.
    Returns (rows, period_label).
    """
    query = text("""
        WITH latest AS (
            SELECT
                EXTRACT(YEAR  FROM MAX(start_date))::INT AS yr,
                EXTRACT(MONTH FROM MAX(start_date))::INT AS mo
            FROM campaigns
        )
        SELECT
            cam.platform,
            latest.yr                                     AS data_year,
            latest.mo                                     AS data_month,
            COUNT(cam.campaign_id)                        AS total_campaigns,
            ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
            ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS avg_ctr,
            ROUND(AVG(cam.cpc)::NUMERIC, 2)               AS avg_cpc,
            ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)   AS avg_conversion_rate,
            ROUND(AVG(cam.engagement_rate)::NUMERIC, 5)   AS avg_engagement_rate,
            ROUND(AVG(cam.sentiment_score)::NUMERIC, 3)   AS avg_sentiment,
            ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
            ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS total_ad_spend,
            p.avg_market_ctr                              AS market_benchmark_ctr
        FROM campaigns cam
        JOIN platforms p ON cam.platform = p.platform_name
        CROSS JOIN latest
        WHERE EXTRACT(YEAR  FROM cam.start_date) = latest.yr
          AND EXTRACT(MONTH FROM cam.start_date) = latest.mo
        GROUP BY cam.platform, p.avg_market_ctr, latest.yr, latest.mo
        ORDER BY total_revenue DESC
    """)

    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]

    period = ""
    if data:
        period = f"{data[0]['data_year']}-{str(data[0]['data_month']).zfill(2)}"

    return data, period


def _fetch_period_changes_all(db: Session) -> dict[str, dict]:
    """
    Fetch month-over-month changes for ALL platforms.
    Returns dict keyed by platform name.
    """
    query = text("""
        WITH latest AS (
            SELECT
                EXTRACT(YEAR  FROM MAX(start_date))::INT AS yr,
                EXTRACT(MONTH FROM MAX(start_date))::INT AS mo
            FROM campaigns
        ),
        current_period AS (
            SELECT
                cam.platform,
                AVG(cam.roi)::FLOAT               AS avg_roi,
                AVG(cam.roas)::FLOAT              AS avg_roas,
                AVG(cam.ctr)::FLOAT               AS avg_ctr,
                SUM(cam.revenue_generated)::FLOAT AS total_revenue,
                AVG(cam.conversion_rate)::FLOAT   AS avg_conv_rate
            FROM campaigns cam, latest
            WHERE EXTRACT(YEAR  FROM cam.start_date) = latest.yr
              AND EXTRACT(MONTH FROM cam.start_date) = latest.mo
            GROUP BY cam.platform
        ),
        previous_period AS (
            SELECT
                cam.platform,
                AVG(cam.roi)::FLOAT               AS avg_roi,
                AVG(cam.roas)::FLOAT              AS avg_roas,
                AVG(cam.ctr)::FLOAT               AS avg_ctr,
                SUM(cam.revenue_generated)::FLOAT AS total_revenue,
                AVG(cam.conversion_rate)::FLOAT   AS avg_conv_rate
            FROM campaigns cam, latest
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
            c.platform,
            c.avg_roi        AS curr_roi,
            p.avg_roi        AS prev_roi,
            c.avg_roas       AS curr_roas,
            p.avg_roas       AS prev_roas,
            c.avg_ctr        AS curr_ctr,
            p.avg_ctr        AS prev_ctr,
            c.total_revenue  AS curr_revenue,
            p.total_revenue  AS prev_revenue,
            c.avg_conv_rate  AS curr_conv,
            p.avg_conv_rate  AS prev_conv
        FROM current_period  c
        LEFT JOIN previous_period p ON c.platform = p.platform
    """)

    rows = db.execute(query).mappings().all()
    return {row["platform"]: dict(row) for row in rows}


# ─────────────────────────────────────────────────────────────
# Alert generators — one per metric category
# ─────────────────────────────────────────────────────────────
def _check_roas_alerts(row: dict, alerts: list[Alert]):
    plat = row["platform"]
    roas = _f(row["avg_roas"])

    if roas < THRESHOLDS["roas_critical"]:
        alerts.append(Alert(
            severity="CRITICAL",
            platform=plat,
            metric="ROAS",
            current_value=f"{roas:.4f}",
            threshold=f"< {THRESHOLDS['roas_critical']}",
            message=(
                f"{plat} ROAS is {roas:.4f} — below critical threshold. "
                f"Generating less than ${roas:.2f} per $1 spent."
            ),
            action="Pause underperforming ad sets. Reallocate budget immediately.",
        ))
    elif roas < THRESHOLDS["roas_warning"]:
        alerts.append(Alert(
            severity="WARNING",
            platform=plat,
            metric="ROAS",
            current_value=f"{roas:.4f}",
            threshold=f"< {THRESHOLDS['roas_warning']}",
            message=f"{plat} ROAS is {roas:.4f} — below recommended 3.0.",
            action="Review targeting and bidding. Test new creatives.",
        ))


def _check_ctr_alerts(row: dict, alerts: list[Alert]):
    plat      = row["platform"]
    ctr       = _f(row["avg_ctr"])
    benchmark = _f(row["market_benchmark_ctr"])

    if ctr < THRESHOLDS["ctr_critical"]:
        alerts.append(Alert(
            severity="CRITICAL",
            platform=plat,
            metric="CTR",
            current_value=f"{ctr:.5f}",
            threshold=f"< {THRESHOLDS['ctr_critical']}",
            message=(
                f"{plat} CTR is critically low at {ctr:.5f}. "
                f"Market benchmark: {benchmark:.5f}."
            ),
            action="Stop current creatives. Launch A/B test immediately.",
        ))
    elif ctr < THRESHOLDS["ctr_warning"]:
        alerts.append(Alert(
            severity="WARNING",
            platform=plat,
            metric="CTR",
            current_value=f"{ctr:.5f}",
            threshold=f"< {THRESHOLDS['ctr_warning']}",
            message=f"{plat} CTR is {ctr:.5f} — below 1% benchmark.",
            action="Refresh ad creative. Review audience targeting.",
        ))

    if benchmark > 0:
        diff_pct = ((ctr - benchmark) / benchmark) * 100
        if diff_pct < -20:
            alerts.append(Alert(
                severity="WARNING",
                platform=plat,
                metric="CTR vs Market Benchmark",
                current_value=f"{ctr:.5f}",
                threshold=f"market: {benchmark:.5f}",
                message=(
                    f"{plat} CTR is {abs(diff_pct):.1f}% "
                    f"below market benchmark."
                ),
                action="Conduct competitive creative analysis this week.",
            ))


def _check_conversion_alerts(row: dict, alerts: list[Alert]):
    plat      = row["platform"]
    conv_rate = _f(row["avg_conversion_rate"])

    if conv_rate < THRESHOLDS["conv_critical"]:
        alerts.append(Alert(
            severity="CRITICAL",
            platform=plat,
            metric="Conversion Rate",
            current_value=f"{conv_rate:.5f}",
            threshold=f"< {THRESHOLDS['conv_critical']}",
            message=(
                f"{plat} conversion rate is {conv_rate:.5f} — "
                f"below 1%. Sales funnel is broken."
            ),
            action=(
                "Audit landing page immediately. "
                "Check for broken UX, slow load, misaligned offer."
            ),
        ))
    elif conv_rate < THRESHOLDS["conv_warning"]:
        alerts.append(Alert(
            severity="WARNING",
            platform=plat,
            metric="Conversion Rate",
            current_value=f"{conv_rate:.5f}",
            threshold=f"< {THRESHOLDS['conv_warning']}",
            message=f"{plat} conversion rate {conv_rate:.5f} is below 2%.",
            action="Test new landing page copy and CTA. Add social proof.",
        ))


def _check_cpc_alerts(row: dict, alerts: list[Alert]):
    plat = row["platform"]
    cpc  = _f(row["avg_cpc"])

    if cpc > THRESHOLDS["cpc_critical"]:
        alerts.append(Alert(
            severity="CRITICAL",
            platform=plat,
            metric="CPC",
            current_value=f"${cpc:.2f}",
            threshold=f"> ${THRESHOLDS['cpc_critical']}",
            message=(
                f"{plat} CPC is ${cpc:.2f} — "
                f"critically high. Traffic cost is unsustainable."
            ),
            action=(
                "Switch to narrow audience targeting. "
                "Use lookalike audiences. Review bidding strategy."
            ),
        ))
    elif cpc > THRESHOLDS["cpc_warning"]:
        alerts.append(Alert(
            severity="WARNING",
            platform=plat,
            metric="CPC",
            current_value=f"${cpc:.2f}",
            threshold=f"> ${THRESHOLDS['cpc_warning']}",
            message=f"{plat} CPC is ${cpc:.2f} — above $5 warning level.",
            action="Review audience overlap. Test manual vs auto bidding.",
        ))


def _check_engagement_alerts(row: dict, alerts: list[Alert]):
    plat       = row["platform"]
    eng_rate   = _f(row["avg_engagement_rate"])
    sentiment  = _f(row["avg_sentiment"])

    if eng_rate < THRESHOLDS["engagement_critical"]:
        alerts.append(Alert(
            severity="CRITICAL",
            platform=plat,
            metric="Engagement Rate",
            current_value=f"{eng_rate:.5f}",
            threshold=f"< {THRESHOLDS['engagement_critical']}",
            message=(
                f"{plat} engagement rate is {eng_rate:.5f} — "
                f"critically low. Audience not responding."
            ),
            action=(
                "Overhaul content strategy. "
                "Test interactive formats: polls, stories, Q&A."
            ),
        ))
    elif eng_rate < THRESHOLDS["engagement_warning"]:
        alerts.append(Alert(
            severity="WARNING",
            platform=plat,
            metric="Engagement Rate",
            current_value=f"{eng_rate:.5f}",
            threshold=f"< {THRESHOLDS['engagement_warning']}",
            message=f"{plat} engagement rate {eng_rate:.5f} is below 2%.",
            action="Increase video content. Post at peak hours.",
        ))

    if sentiment < THRESHOLDS["sentiment_negative"]:
        alerts.append(Alert(
            severity="CRITICAL",
            platform=plat,
            metric="Sentiment Score",
            current_value=f"{sentiment:.3f}",
            threshold=f"< {THRESHOLDS['sentiment_negative']}",
            message=(
                f"{plat} sentiment score is {sentiment:.3f} — "
                f"negative audience sentiment detected."
            ),
            action=(
                "Review ad comments immediately. "
                "Pause ads receiving negative feedback."
            ),
        ))


def _check_period_change_alerts(
    changes: dict,
    alerts: list[Alert],
):
    """Check month-over-month drops across all platforms."""
    for platform, comp in changes.items():
        roi_change = _pct_change(
            _f(comp.get("curr_roi")),
            _f(comp.get("prev_roi")),
        )
        rev_change = _pct_change(
            _f(comp.get("curr_revenue")),
            _f(comp.get("prev_revenue")),
        )

        if roi_change is not None:
            if roi_change <= THRESHOLDS["drop_critical"]:
                alerts.append(Alert(
                    severity="CRITICAL",
                    platform=platform,
                    metric="ROI Month-over-Month",
                    current_value=f"{comp.get('curr_roi', 0):.4f}",
                    threshold=f"> {abs(THRESHOLDS['drop_critical'])}% drop",
                    message=(
                        f"{platform} ROI dropped {abs(roi_change):.1f}% "
                        f"vs previous month."
                    ),
                    action=(
                        "Audit top campaigns by spend. "
                        "Pause campaigns with ROI below 0.5."
                    ),
                ))
            elif roi_change <= THRESHOLDS["drop_warning"]:
                alerts.append(Alert(
                    severity="WARNING",
                    platform=platform,
                    metric="ROI Month-over-Month",
                    current_value=f"{comp.get('curr_roi', 0):.4f}",
                    threshold=f"> {abs(THRESHOLDS['drop_warning'])}% drop",
                    message=(
                        f"{platform} ROI declined {abs(roi_change):.1f}% "
                        f"vs previous month."
                    ),
                    action="Monitor for 2 weeks. Review recent campaign changes.",
                ))

        if rev_change is not None and rev_change <= THRESHOLDS["drop_critical"]:
            alerts.append(Alert(
                severity="CRITICAL",
                platform=platform,
                metric="Revenue Month-over-Month",
                current_value=f"${comp.get('curr_revenue', 0):,.2f}",
                threshold=f"> {abs(THRESHOLDS['drop_critical'])}% drop",
                message=(
                    f"{platform} revenue dropped {abs(rev_change):.1f}% "
                    f"vs previous month."
                ),
                action=(
                    "Launch recovery campaign targeting warm audiences. "
                    "Review pricing and offer alignment."
                ),
            ))


# ─────────────────────────────────────────────────────────────
# MASTER ALERT SCANNER
# ─────────────────────────────────────────────────────────────
def scan_all_alerts(db: Session) -> AlertReport:
    """
    Scan ALL platforms and return a complete alert report.
    Zero LLM calls — pure rule engine.
    Fast enough to poll every few minutes from a dashboard.
    """
    report = AlertReport()

    try:
        # Fetch all platform metrics
        metrics, period = _fetch_all_platform_metrics(db)
        report.platforms_scanned = len(metrics)
        report.data_period       = period

        # Run all alert checks per platform
        for row in metrics:
            _check_roas_alerts(row,       report.alerts)
            _check_ctr_alerts(row,        report.alerts)
            _check_conversion_alerts(row, report.alerts)
            _check_cpc_alerts(row,        report.alerts)
            _check_engagement_alerts(row, report.alerts)

        # Run period-change checks across all platforms
        changes = _fetch_period_changes_all(db)
        _check_period_change_alerts(changes, report.alerts)

        # Count by severity
        report.critical_count = sum(
            1 for a in report.alerts if a.severity == "CRITICAL"
        )
        report.warning_count = sum(
            1 for a in report.alerts if a.severity == "WARNING"
        )

        logger.info(
            f"Alert scan complete | period={period} "
            f"| platforms={report.platforms_scanned} "
            f"| critical={report.critical_count} "
            f"| warnings={report.warning_count}"
        )

    except Exception as e:
        logger.error(f"Alert scan error: {e}", exc_info=True)

    return report