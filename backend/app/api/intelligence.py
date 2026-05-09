"""Business Intelligence Endpoints — CAC, Funnels, YoY Growth"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/intelligence", tags=["Business Intelligence"])


@router.get("/cac-by-platform", response_model=APIResponse)
def get_cac_by_platform(db: Session = Depends(get_db)):
    """Customer Acquisition Cost (CAC) per platform."""
    query = text("""
        SELECT
            cam.platform,
            ROUND(SUM(cam.ad_spend)::NUMERIC, 2)       AS total_ad_spend,
            COUNT(cv.conversion_id)                    AS total_conversions,
            COUNT(CASE WHEN cv.repeat_customer = FALSE
                       THEN 1 END)                     AS new_customers,
            ROUND(SUM(cam.ad_spend) /
                NULLIF(COUNT(CASE WHEN cv.repeat_customer = FALSE
                                  THEN 1 END), 0)
            ::NUMERIC, 2)                              AS cac
        FROM campaigns cam
        LEFT JOIN conversions cv ON cam.campaign_id = cv.campaign_id
        GROUP BY cam.platform
        ORDER BY cac ASC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="CAC by platform fetched",
        data=data, total_records=len(data),
    )


@router.get("/conversion-funnel", response_model=APIResponse)
def get_conversion_funnel(db: Session = Depends(get_db)):
    """Impressions → Clicks → Conversions funnel per platform."""
    query = text("""
        SELECT
            platform,
            SUM(impressions)                            AS total_impressions,
            SUM(clicks)                                 AS total_clicks,
            SUM(conversions)                            AS total_conversions,
            ROUND(SUM(clicks) * 100.0
                / NULLIF(SUM(impressions), 0)::NUMERIC, 4) AS impression_to_click_pct,
            ROUND(SUM(conversions) * 100.0
                / NULLIF(SUM(clicks), 0)::NUMERIC, 4)     AS click_to_conversion_pct,
            ROUND(SUM(conversions) * 100.0
                / NULLIF(SUM(impressions), 0)::NUMERIC, 6) AS overall_funnel_pct
        FROM campaigns
        GROUP BY platform
        ORDER BY overall_funnel_pct DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Conversion funnel fetched",
        data=data, total_records=len(data),
    )


@router.get("/yoy-growth", response_model=APIResponse)
def get_yoy_growth(db: Session = Depends(get_db)):
    """Year-over-Year revenue growth using window functions."""
    query = text("""
        WITH yearly AS (
            SELECT
                c.year,
                ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS annual_revenue
            FROM campaigns cam
            JOIN calendar c ON cam.start_date = c.date
            GROUP BY c.year
        )
        SELECT
            year,
            annual_revenue,
            LAG(annual_revenue) OVER (ORDER BY year)  AS prev_year_revenue,
            ROUND(
                (annual_revenue - LAG(annual_revenue) OVER (ORDER BY year))
                * 100.0
                / NULLIF(LAG(annual_revenue) OVER (ORDER BY year), 0)
            ::NUMERIC, 2)                             AS yoy_growth_pct
        FROM yearly
        ORDER BY year
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="YoY growth fetched",
        data=data, total_records=len(data),
    )


@router.get("/refund-analysis", response_model=APIResponse)
def get_refund_analysis(db: Session = Depends(get_db)):
    """Refund rate and revenue impact analysis."""
    query = text("""
        SELECT
            refund_status,
            COUNT(conversion_id)                     AS total_conversions,
            ROUND(SUM(order_value)::NUMERIC, 2)      AS gross_revenue,
            ROUND(SUM(profit_amount)::NUMERIC, 2)    AS gross_profit,
            ROUND(AVG(order_value)::NUMERIC, 2)      AS avg_order_value,
            ROUND(COUNT(conversion_id) * 100.0
                / SUM(COUNT(conversion_id)) OVER ()
            ::NUMERIC, 2)                            AS pct_of_total
        FROM conversions
        GROUP BY refund_status
        ORDER BY total_conversions DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Refund analysis fetched",
        data=data, total_records=len(data),
    )