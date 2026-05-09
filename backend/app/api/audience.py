"""Audience Insights Endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/audience", tags=["Audience Insights"])


@router.get("/by-age-group", response_model=APIResponse)
def get_by_age_group(db: Session = Depends(get_db)):
    """Conversion rate and performance by targeted age group."""
    query = text("""
        SELECT
            audience_age_group,
            COUNT(campaign_id)                       AS total_campaigns,
            SUM(conversions)                         AS total_conversions,
            ROUND(AVG(conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
            ROUND(AVG(ctr)::NUMERIC, 5)              AS avg_ctr,
            ROUND(AVG(roas)::NUMERIC, 4)             AS avg_roas
        FROM campaigns
        GROUP BY audience_age_group
        ORDER BY avg_conversion_rate DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Audience age group performance fetched",
        data=data, total_records=len(data),
    )


@router.get("/by-device", response_model=APIResponse)
def get_by_device(db: Session = Depends(get_db)):
    """Mobile vs Desktop vs Tablet performance comparison."""
    query = text("""
        SELECT
            device_type,
            COUNT(campaign_id)                       AS total_campaigns,
            ROUND(AVG(ctr)::NUMERIC, 5)              AS avg_ctr,
            ROUND(AVG(conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
            ROUND(AVG(roas)::NUMERIC, 4)             AS avg_roas,
            ROUND(AVG(roi)::NUMERIC, 4)              AS avg_roi,
            SUM(conversions)                         AS total_conversions
        FROM campaigns
        GROUP BY device_type
        ORDER BY avg_conversion_rate DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Device performance fetched",
        data=data, total_records=len(data),
    )


@router.get("/by-income-level", response_model=APIResponse)
def get_by_income_level(db: Session = Depends(get_db)):
    """Order value and profit by customer income level."""
    query = text("""
        SELECT
            cu.income_level,
            COUNT(cv.conversion_id)                   AS total_conversions,
            ROUND(AVG(cv.order_value)::NUMERIC, 2)    AS avg_order_value,
            ROUND(AVG(cv.profit_amount)::NUMERIC, 2)  AS avg_profit,
            ROUND(SUM(cv.order_value)::NUMERIC, 2)    AS total_revenue,
            SUM(CASE WHEN cv.discount_used THEN 1 ELSE 0 END) AS discount_used_count,
            ROUND(AVG(cv.discount_pct)::NUMERIC, 1)   AS avg_discount_pct
        FROM conversions cv
        JOIN customers cu ON cv.customer_id = cu.customer_id
        GROUP BY cu.income_level
        ORDER BY avg_order_value DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Income level analysis fetched",
        data=data, total_records=len(data),
    )


@router.get("/by-gender", response_model=APIResponse)
def get_by_gender(db: Session = Depends(get_db)):
    """Performance comparison by audience gender targeting."""
    query = text("""
        SELECT
            audience_gender,
            COUNT(campaign_id)                        AS total_campaigns,
            ROUND(AVG(ctr)::NUMERIC, 5)               AS avg_ctr,
            ROUND(AVG(conversion_rate)::NUMERIC, 5)   AS avg_conversion_rate,
            ROUND(AVG(roas)::NUMERIC, 4)              AS avg_roas,
            ROUND(SUM(revenue_generated)::NUMERIC, 2) AS total_revenue
        FROM campaigns
        GROUP BY audience_gender
        ORDER BY avg_roas DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Gender performance fetched",
        data=data, total_records=len(data),
    )