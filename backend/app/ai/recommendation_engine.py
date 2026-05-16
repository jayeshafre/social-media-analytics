"""
Recommendation Engine — Phase 4.

Deterministic rule-based system that evaluates KPI data
and generates specific, actionable recommendations.

Architecture principle:
- Rules are hardcoded business logic (not AI guesses)
- Thresholds are based on marketing industry standards
- Every recommendation has: trigger, severity, action
- LLM only formats and explains — never invents recommendations

Recommendation severity levels:
- CRITICAL : Immediate action required
- WARNING  : Monitor and plan action
- POSITIVE : Performing well, consider scaling
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger("sma_api.recommendation_engine")


# ─────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────
@dataclass
class Recommendation:
    severity: str       # CRITICAL | WARNING | POSITIVE
    category: str       # budget | creative | audience | platform | engagement
    metric:   str       # which KPI triggered this
    finding:  str       # what was found (with real numbers)
    action:   str       # specific action to take


@dataclass
class RecommendationReport:
    platform:        Optional[str]
    time_period:     Optional[str]
    recommendations: list[Recommendation] = field(default_factory=list)
    summary:         str = ""

    def has_recommendations(self) -> bool:
        return len(self.recommendations) > 0

    def formatted(self) -> str:
        """Format the report as clean text for prompt injection."""
        if not self.recommendations:
            return "No specific recommendations generated."

        lines = ["RECOMMENDATIONS FROM RULE ENGINE:"]

        # Group by severity for clarity
        for severity in ["CRITICAL", "WARNING", "POSITIVE"]:
            group = [r for r in self.recommendations if r.severity == severity]
            if not group:
                continue

            emoji = {"CRITICAL": "🔴", "WARNING": "🟡", "POSITIVE": "🟢"}[severity]
            lines.append(f"\n{emoji} {severity}:")

            for rec in group:
                lines.append(f"  [{rec.category.upper()}] {rec.metric}")
                lines.append(f"  Finding : {rec.finding}")
                lines.append(f"  Action  : {rec.action}")

        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Industry benchmark thresholds
# These are the rules — adjust as your business learns
# ─────────────────────────────────────────────────────────────
THRESHOLDS = {
    # ROAS thresholds
    "roas_critical":   2.0,   # Below this = losing money effectively
    "roas_warning":    3.0,   # Below this = underperforming
    "roas_good":       5.0,   # Above this = strong performance
    "roas_excellent":  8.0,   # Above this = scale immediately

    # ROI thresholds
    "roi_critical":    0.5,   # Below 50% ROI = serious problem
    "roi_warning":     1.0,   # Below 100% ROI = needs attention
    "roi_good":        2.0,   # Above 200% ROI = healthy
    "roi_excellent":   4.0,   # Above 400% ROI = scale budget

    # CTR thresholds (as ratio, not percentage)
    "ctr_critical":    0.005,  # Below 0.5% CTR = creative problem
    "ctr_warning":     0.01,   # Below 1% CTR = needs refresh
    "ctr_good":        0.03,   # Above 3% CTR = strong creative

    # Conversion rate thresholds
    "conv_critical":   0.01,   # Below 1% = funnel broken
    "conv_warning":    0.02,   # Below 2% = funnel weak
    "conv_good":       0.05,   # Above 5% = strong funnel

    # CPC thresholds
    "cpc_warning":     5.0,    # Above $5 CPC = expensive traffic
    "cpc_critical":    10.0,   # Above $10 CPC = critical overspend

    # Period-over-period change thresholds
    "drop_critical":   -20.0,  # >20% drop = critical
    "drop_warning":    -10.0,  # >10% drop = warning
    "gain_positive":    10.0,  # >10% gain = positive signal
    "gain_excellent":   25.0,  # >25% gain = scale opportunity

    # Engagement rate thresholds
    "engagement_critical": 0.01,  # Below 1% = very low engagement
    "engagement_warning":  0.02,  # Below 2% = below average
    "engagement_good":     0.05,  # Above 5% = strong engagement

    # Sentiment thresholds
    "sentiment_negative":  -0.1,  # Below -0.1 = negative sentiment
    "sentiment_neutral":    0.1,  # Below 0.1 = neutral
    "sentiment_positive":   0.3,  # Above 0.3 = positive
}


# ─────────────────────────────────────────────────────────────
# Helper: safe float conversion
# ─────────────────────────────────────────────────────────────
def _f(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _pct_change(current: float, previous: float) -> Optional[float]:
    """Calculate percentage change. Returns None if previous is 0."""
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100


# ─────────────────────────────────────────────────────────────
# RULE EVALUATORS
# Each function evaluates one domain and returns recommendations
# ─────────────────────────────────────────────────────────────

def _evaluate_roas(
    roas: float,
    platform: str,
    report: RecommendationReport,
):
    """Evaluate ROAS and generate budget recommendations."""
    if roas < THRESHOLDS["roas_critical"]:
        report.recommendations.append(Recommendation(
            severity="CRITICAL",
            category="budget",
            metric="ROAS",
            finding=(
                f"{platform} ROAS is {roas:.4f} — "
                f"below the critical threshold of {THRESHOLDS['roas_critical']}. "
                f"You are generating less than ${roas:.2f} for every $1 spent."
            ),
            action=(
                "Pause underperforming ad sets immediately. "
                "Reallocate budget to campaigns with ROAS > 3.0. "
                "Review targeting — audience may be too broad or misaligned."
            ),
        ))
    elif roas < THRESHOLDS["roas_warning"]:
        report.recommendations.append(Recommendation(
            severity="WARNING",
            category="budget",
            metric="ROAS",
            finding=(
                f"{platform} ROAS is {roas:.4f} — "
                f"below the recommended threshold of {THRESHOLDS['roas_warning']}. "
                f"Performance is suboptimal."
            ),
            action=(
                "Review campaign targeting and bidding strategy. "
                "Test new ad creatives. Consider reducing budget by 20% "
                "until ROAS improves above 3.0."
            ),
        ))
    elif roas >= THRESHOLDS["roas_excellent"]:
        report.recommendations.append(Recommendation(
            severity="POSITIVE",
            category="budget",
            metric="ROAS",
            finding=(
                f"{platform} ROAS is {roas:.4f} — "
                f"excellent performance above {THRESHOLDS['roas_excellent']}."
            ),
            action=(
                "Scale budget on this platform by 20-30%. "
                "Duplicate top-performing campaigns to new audience segments. "
                "This platform is your highest efficiency channel."
            ),
        ))
    elif roas >= THRESHOLDS["roas_good"]:
        report.recommendations.append(Recommendation(
            severity="POSITIVE",
            category="budget",
            metric="ROAS",
            finding=(
                f"{platform} ROAS is {roas:.4f} — "
                f"performing well above {THRESHOLDS['roas_good']}."
            ),
            action=(
                "Maintain current budget. Consider a 10-15% increase "
                "on top-performing ad sets to capture more volume."
            ),
        ))


def _evaluate_ctr(
    ctr: float,
    market_benchmark: float,
    platform: str,
    report: RecommendationReport,
):
    """Evaluate CTR vs market benchmark and generate creative recommendations."""
    if ctr < THRESHOLDS["ctr_critical"]:
        report.recommendations.append(Recommendation(
            severity="CRITICAL",
            category="creative",
            metric="CTR",
            finding=(
                f"{platform} CTR is {ctr:.5f} — "
                f"critically low (below {THRESHOLDS['ctr_critical']}). "
                f"Market benchmark is {market_benchmark:.5f}."
            ),
            action=(
                "Stop current ad creatives immediately. "
                "Launch A/B test with 3 new creative concepts. "
                "Review ad copy, imagery, and call-to-action. "
                "Consider video ads which typically outperform static."
            ),
        ))
    elif ctr < THRESHOLDS["ctr_warning"]:
        report.recommendations.append(Recommendation(
            severity="WARNING",
            category="creative",
            metric="CTR",
            finding=(
                f"{platform} CTR is {ctr:.5f} — "
                f"below 1% and underperforming. "
                f"Market benchmark: {market_benchmark:.5f}."
            ),
            action=(
                "Refresh ad creative within 2 weeks. "
                "Test stronger headlines and clearer CTAs. "
                "Review audience targeting for relevance alignment."
            ),
        ))

    # Benchmark comparison
    if market_benchmark > 0:
        benchmark_diff_pct = ((ctr - market_benchmark) / market_benchmark) * 100
        if benchmark_diff_pct < -20:
            report.recommendations.append(Recommendation(
                severity="WARNING",
                category="creative",
                metric="CTR vs Benchmark",
                finding=(
                    f"{platform} CTR is {abs(benchmark_diff_pct):.1f}% "
                    f"below market benchmark "
                    f"({ctr:.5f} vs {market_benchmark:.5f})."
                ),
                action=(
                    "Conduct competitive creative analysis. "
                    "Review what top performers in your category are doing. "
                    "Prioritize creative testing this month."
                ),
            ))
        elif benchmark_diff_pct > 20:
            report.recommendations.append(Recommendation(
                severity="POSITIVE",
                category="creative",
                metric="CTR vs Benchmark",
                finding=(
                    f"{platform} CTR is {benchmark_diff_pct:.1f}% "
                    f"above market benchmark — strong creative performance."
                ),
                action=(
                    "Document what is working in this creative. "
                    "Apply the same creative strategy to other platforms. "
                    "Scale spend on this creative before fatigue sets in."
                ),
            ))


def _evaluate_conversion_rate(
    conv_rate: float,
    platform: str,
    report: RecommendationReport,
):
    """Evaluate conversion rate and generate funnel recommendations."""
    if conv_rate < THRESHOLDS["conv_critical"]:
        report.recommendations.append(Recommendation(
            severity="CRITICAL",
            category="audience",
            metric="Conversion Rate",
            finding=(
                f"{platform} conversion rate is {conv_rate:.5f} — "
                f"critically low (below 1%). "
                f"The sales funnel is severely underperforming."
            ),
            action=(
                "Audit the landing page experience immediately. "
                "Check for broken links, slow load times, or UX issues. "
                "Review audience targeting — traffic may be unqualified. "
                "Implement retargeting campaigns for engaged non-converters."
            ),
        ))
    elif conv_rate < THRESHOLDS["conv_warning"]:
        report.recommendations.append(Recommendation(
            severity="WARNING",
            category="audience",
            metric="Conversion Rate",
            finding=(
                f"{platform} conversion rate is {conv_rate:.5f} — "
                f"below the 2% recommended threshold."
            ),
            action=(
                "Review landing page copy and offer alignment. "
                "Test different CTAs and value propositions. "
                "Add social proof (reviews, testimonials) to landing page. "
                "Consider discount or urgency trigger for fence-sitters."
            ),
        ))
    elif conv_rate >= THRESHOLDS["conv_good"]:
        report.recommendations.append(Recommendation(
            severity="POSITIVE",
            category="audience",
            metric="Conversion Rate",
            finding=(
                f"{platform} conversion rate is {conv_rate:.5f} — "
                f"above 5%, which is excellent funnel performance."
            ),
            action=(
                "Scale traffic to this funnel. "
                "Increase top-of-funnel budget to feed more users "
                "into this high-converting flow. "
                "Replicate this funnel structure on other platforms."
            ),
        ))


def _evaluate_cpc(
    cpc: float,
    platform: str,
    report: RecommendationReport,
):
    """Evaluate CPC and generate cost efficiency recommendations."""
    if cpc > THRESHOLDS["cpc_critical"]:
        report.recommendations.append(Recommendation(
            severity="CRITICAL",
            category="budget",
            metric="CPC",
            finding=(
                f"{platform} CPC is ${cpc:.2f} — "
                f"critically high (above ${THRESHOLDS['cpc_critical']}). "
                f"Traffic acquisition cost is unsustainable."
            ),
            action=(
                "Switch from broad to narrow audience targeting. "
                "Use lookalike audiences based on your top converters. "
                "Review bidding strategy — switch to target CPA if available. "
                "Pause highest-CPC ad sets immediately."
            ),
        ))
    elif cpc > THRESHOLDS["cpc_warning"]:
        report.recommendations.append(Recommendation(
            severity="WARNING",
            category="budget",
            metric="CPC",
            finding=(
                f"{platform} CPC is ${cpc:.2f} — "
                f"above the ${THRESHOLDS['cpc_warning']} warning threshold."
            ),
            action=(
                "Review audience overlap — you may be bidding against yourself. "
                "Test manual bidding vs automated bidding. "
                "Improve Quality Score / Relevance Score to lower CPC naturally."
            ),
        ))


def _evaluate_engagement(
    engagement_rate: float,
    sentiment_score: float,
    platform: str,
    report: RecommendationReport,
):
    """Evaluate engagement rate and sentiment score."""
    if engagement_rate < THRESHOLDS["engagement_critical"]:
        report.recommendations.append(Recommendation(
            severity="CRITICAL",
            category="engagement",
            metric="Engagement Rate",
            finding=(
                f"{platform} engagement rate is {engagement_rate:.5f} — "
                f"critically low (below 1%). "
                f"Audience is not responding to content."
            ),
            action=(
                "Complete content strategy overhaul needed. "
                "Survey your audience about content preferences. "
                "Test interactive formats: polls, stories, Q&A. "
                "Review posting frequency — may be causing fatigue."
            ),
        ))
    elif engagement_rate < THRESHOLDS["engagement_warning"]:
        report.recommendations.append(Recommendation(
            severity="WARNING",
            category="engagement",
            metric="Engagement Rate",
            finding=(
                f"{platform} engagement rate is {engagement_rate:.5f} — "
                f"below 2% average benchmark."
            ),
            action=(
                "Introduce more interactive content formats. "
                "Increase video content ratio. "
                "Post during peak audience activity hours. "
                "Engage with comments to boost algorithmic reach."
            ),
        ))

    # Sentiment evaluation
    if sentiment_score < THRESHOLDS["sentiment_negative"]:
        report.recommendations.append(Recommendation(
            severity="CRITICAL",
            category="engagement",
            metric="Sentiment Score",
            finding=(
                f"{platform} sentiment score is {sentiment_score:.3f} — "
                f"negative audience sentiment detected."
            ),
            action=(
                "Review all recent ad comments immediately. "
                "Identify and address specific audience complaints. "
                "Pause ads receiving negative feedback. "
                "Consider a brand safety audit."
            ),
        ))


def _evaluate_period_changes(
    curr_roi: float,
    prev_roi: float,
    curr_revenue: float,
    prev_revenue: float,
    curr_conv: float,
    prev_conv: float,
    platform: str,
    report: RecommendationReport,
):
    """
    Evaluate period-over-period changes.
    This is the anomaly-specific rule set.
    """
    roi_change  = _pct_change(curr_roi,     prev_roi)
    rev_change  = _pct_change(curr_revenue, prev_revenue)
    conv_change = _pct_change(curr_conv,    prev_conv)

    # ROI change evaluation
    if roi_change is not None:
        if roi_change <= THRESHOLDS["drop_critical"]:
            report.recommendations.append(Recommendation(
                severity="CRITICAL",
                category="budget",
                metric="ROI Period Change",
                finding=(
                    f"{platform} ROI dropped {abs(roi_change):.1f}% "
                    f"from {prev_roi:.4f} to {curr_roi:.4f}. "
                    f"This is a critical decline requiring immediate action."
                ),
                action=(
                    "Immediately audit top 10 campaigns by spend. "
                    "Pause campaigns with ROI below 0.5. "
                    "Identify if this is platform-wide or campaign-specific. "
                    "Check for audience saturation — frequency may be too high. "
                    "Review if a competitor launched a major campaign."
                ),
            ))
        elif roi_change <= THRESHOLDS["drop_warning"]:
            report.recommendations.append(Recommendation(
                severity="WARNING",
                category="budget",
                metric="ROI Period Change",
                finding=(
                    f"{platform} ROI declined {abs(roi_change):.1f}% "
                    f"from {prev_roi:.4f} to {curr_roi:.4f}."
                ),
                action=(
                    "Monitor closely over next 2 weeks. "
                    "Review recent campaign changes — new creatives, "
                    "targeting updates, or budget shifts may be the cause. "
                    "Compare by campaign type to isolate the issue."
                ),
            ))
        elif roi_change >= THRESHOLDS["gain_excellent"]:
            report.recommendations.append(Recommendation(
                severity="POSITIVE",
                category="budget",
                metric="ROI Period Change",
                finding=(
                    f"{platform} ROI grew {roi_change:.1f}% "
                    f"from {prev_roi:.4f} to {curr_roi:.4f} — excellent growth."
                ),
                action=(
                    "Identify which campaigns drove this improvement. "
                    "Scale their budget by 20-30%. "
                    "Document the strategy for replication on other platforms."
                ),
            ))

    # Revenue change evaluation
    if rev_change is not None and rev_change <= THRESHOLDS["drop_critical"]:
        report.recommendations.append(Recommendation(
            severity="CRITICAL",
            category="budget",
            metric="Revenue Period Change",
            finding=(
                f"{platform} revenue dropped {abs(rev_change):.1f}% "
                f"(${prev_revenue:,.2f} → ${curr_revenue:,.2f})."
            ),
            action=(
                "Cross-check with conversion data to confirm the drop. "
                "Review if there were product/pricing changes this period. "
                "Check attribution window — conversions may be delayed. "
                "Launch a recovery campaign targeting warm audiences."
            ),
        ))

    # Conversion rate change evaluation
    if conv_change is not None and conv_change <= THRESHOLDS["drop_warning"]:
        report.recommendations.append(Recommendation(
            severity="WARNING",
            category="audience",
            metric="Conversion Rate Period Change",
            finding=(
                f"{platform} conversion rate dropped {abs(conv_change):.1f}% "
                f"({prev_conv:.5f} → {curr_conv:.5f})."
            ),
            action=(
                "Audit landing page — check for recent changes. "
                "Review audience targeting for quality degradation. "
                "Test a new offer or incentive to recover conversions. "
                "Check if traffic source quality changed this period."
            ),
        ))


# ─────────────────────────────────────────────────────────────
# DATA FETCHERS FOR RECOMMENDATION ENGINE
# These fetch the specific data needed to evaluate rules
# ─────────────────────────────────────────────────────────────
def _fetch_platform_metrics(
    db: Session,
    platform: Optional[str],
) -> list[dict]:
    """Fetch current KPI metrics per platform for rule evaluation."""
    plat_filter = "AND cam.platform = :platform" if platform else ""
    params      = {"platform": platform} if platform else {}

    query = text(f"""
        SELECT
            cam.platform,
            ROUND(AVG(cam.roas)::NUMERIC, 4)             AS avg_roas,
            ROUND(AVG(cam.roi)::NUMERIC, 4)              AS avg_roi,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)              AS avg_ctr,
            ROUND(AVG(cam.cpc)::NUMERIC, 2)              AS avg_cpc,
            ROUND(AVG(cam.conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
            ROUND(AVG(cam.engagement_rate)::NUMERIC, 5)  AS avg_engagement_rate,
            ROUND(AVG(cam.sentiment_score)::NUMERIC, 3)  AS avg_sentiment,
            p.avg_market_ctr                             AS market_benchmark_ctr
        FROM campaigns cam
        JOIN platforms p ON cam.platform = p.platform_name
        WHERE EXTRACT(YEAR  FROM cam.start_date) = (
            SELECT EXTRACT(YEAR  FROM MAX(start_date)) FROM campaigns
        )
        AND EXTRACT(MONTH FROM cam.start_date) = (
            SELECT EXTRACT(MONTH FROM MAX(start_date)) FROM campaigns
        )
        {plat_filter}
        GROUP BY cam.platform, p.avg_market_ctr
    """)

    rows = db.execute(query, params).mappings().all()
    return [dict(r) for r in rows]


def _fetch_period_comparison(
    db: Session,
    platform: Optional[str],
) -> list[dict]:
    """
    Fetch current vs previous month metrics for change evaluation.
    Uses the same data-anchored approach as Phase 3.
    """
    plat_filter = "AND platform = :platform" if platform else ""
    params      = {"platform": platform} if platform else {}

    query = text(f"""
        WITH latest AS (
            SELECT
                EXTRACT(YEAR  FROM MAX(start_date))::INT AS yr,
                EXTRACT(MONTH FROM MAX(start_date))::INT AS mo
            FROM campaigns
            WHERE 1=1
            {'AND platform = :platform' if platform else ''}
        ),
        current_period AS (
            SELECT
                cam.platform,
                AVG(cam.roi)::FLOAT              AS avg_roi,
                SUM(cam.revenue_generated)::FLOAT AS total_revenue,
                AVG(cam.conversion_rate)::FLOAT  AS avg_conv_rate
            FROM campaigns cam, latest
            WHERE EXTRACT(YEAR  FROM cam.start_date) = latest.yr
              AND EXTRACT(MONTH FROM cam.start_date) = latest.mo
            {plat_filter}
            GROUP BY cam.platform
        ),
        previous_period AS (
            SELECT
                cam.platform,
                AVG(cam.roi)::FLOAT              AS avg_roi,
                SUM(cam.revenue_generated)::FLOAT AS total_revenue,
                AVG(cam.conversion_rate)::FLOAT  AS avg_conv_rate
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
            {plat_filter}
            GROUP BY cam.platform
        )
        SELECT
            c.platform,
            c.avg_roi        AS curr_roi,
            p.avg_roi        AS prev_roi,
            c.total_revenue  AS curr_revenue,
            p.total_revenue  AS prev_revenue,
            c.avg_conv_rate  AS curr_conv,
            p.avg_conv_rate  AS prev_conv
        FROM current_period  c
        LEFT JOIN previous_period p ON c.platform = p.platform
    """)

    rows = db.execute(query, params).mappings().all()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# MASTER RECOMMENDATION FUNCTION
# Called by orchestrator
# ─────────────────────────────────────────────────────────────
def generate_recommendations(
    intent: str,
    db: Session,
    platform: Optional[str] = None,
    time_period: Optional[str] = None,
) -> RecommendationReport:
    """
    Master function — generates a full recommendation report.

    1. Fetch relevant metrics from DB
    2. Apply rule evaluators
    3. Return structured RecommendationReport

    Args:
        intent:      Detected intent (determines which rules to apply)
        db:          SQLAlchemy session
        platform:    Detected platform filter
        time_period: Detected time period

    Returns:
        RecommendationReport with all triggered recommendations
    """
    report = RecommendationReport(
        platform=platform,
        time_period=time_period,
    )

    logger.info(
        f"Generating recommendations | intent={intent} "
        f"| platform={platform} | time={time_period}"
    )

    try:
        # Fetch current metrics
        metrics = _fetch_platform_metrics(db=db, platform=platform)

        # Apply per-platform rules
        for row in metrics:
            plat = row["platform"]

            # Always evaluate core KPIs
            _evaluate_roas(
                roas=_f(row["avg_roas"]),
                platform=plat,
                report=report,
            )
            _evaluate_ctr(
                ctr=_f(row["avg_ctr"]),
                market_benchmark=_f(row["market_benchmark_ctr"]),
                platform=plat,
                report=report,
            )
            _evaluate_conversion_rate(
                conv_rate=_f(row["avg_conversion_rate"]),
                platform=plat,
                report=report,
            )
            _evaluate_cpc(
                cpc=_f(row["avg_cpc"]),
                platform=plat,
                report=report,
            )

            # Engagement rules for engagement/anomaly intents
            if intent in ("engagement", "anomaly", "general"):
                _evaluate_engagement(
                    engagement_rate=_f(row["avg_engagement_rate"]),
                    sentiment_score=_f(row["avg_sentiment"]),
                    platform=plat,
                    report=report,
                )

        # Period comparison rules for anomaly intent
        if intent == "anomaly":
            comparisons = _fetch_period_comparison(
                db=db,
                platform=platform,
            )
            for comp in comparisons:
                _evaluate_period_changes(
                    curr_roi=_f(comp.get("curr_roi")),
                    prev_roi=_f(comp.get("prev_roi")),
                    curr_revenue=_f(comp.get("curr_revenue")),
                    prev_revenue=_f(comp.get("prev_revenue")),
                    curr_conv=_f(comp.get("curr_conv")),
                    prev_conv=_f(comp.get("prev_conv")),
                    platform=comp["platform"],
                    report=report,
                )

        # Build summary line
        critical = sum(
            1 for r in report.recommendations if r.severity == "CRITICAL"
        )
        warning  = sum(
            1 for r in report.recommendations if r.severity == "WARNING"
        )
        positive = sum(
            1 for r in report.recommendations if r.severity == "POSITIVE"
        )

        report.summary = (
            f"Rule engine generated {len(report.recommendations)} recommendations: "
            f"{critical} critical, {warning} warnings, {positive} positive signals."
        )

        logger.info(f"Recommendations complete: {report.summary}")

    except Exception as e:
        logger.error(f"Recommendation engine error: {e}", exc_info=True)
        report.summary = "Recommendation engine encountered an error."

    return report