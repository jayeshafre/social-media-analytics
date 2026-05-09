"""
Revenue Analytics Endpoints
All revenue, profit, ROAS, ROI queries exposed as APIs.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/revenue", tags=["Revenue Analytics"])


@router.get("/by-platform", response_model=APIResponse)
def get_revenue_by_platform(db: Session = Depends(get_db)):
    """Total revenue, profit, ROAS and ROI broken down by platform."""
    query = text("""
        SELECT
            platform,
            COUNT(campaign_id)                          AS total_campaigns,
            ROUND(SUM(ad_spend)::NUMERIC, 2)            AS total_ad_spend,
            ROUND(SUM(revenue_generated)::NUMERIC, 2)   AS total_revenue,
            ROUND(SUM(profit_generated)::NUMERIC, 2)    AS total_profit,
            ROUND(AVG(roas)::NUMERIC, 4)                AS avg_roas,
            ROUND(AVG(roi)::NUMERIC, 4)                 AS avg_roi
        FROM campaigns
        GROUP BY platform
        ORDER BY total_revenue DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Revenue by platform fetched successfully",
        data=data,
        total_records=len(data),
    )


@router.get("/monthly-trend", response_model=APIResponse)
def get_monthly_revenue(
    year: Optional[int] = Query(None, description="Filter by year e.g. 2023"),
    db: Session = Depends(get_db),
):
    """Monthly revenue trend — optionally filter by year."""
    base_query = """
        SELECT
            c.year,
            c.month,
            c.month_name,
            c.quarter,
            ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS monthly_revenue,
            ROUND(SUM(cam.profit_generated)::NUMERIC, 2)  AS monthly_profit,
            ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS monthly_ad_spend,
            COUNT(cam.campaign_id)                        AS campaigns_run
        FROM campaigns cam
        JOIN calendar c ON cam.start_date = c.date
        {where}
        GROUP BY c.year, c.month, c.month_name, c.quarter
        ORDER BY c.year, c.month
    """
    where = "WHERE c.year = :year" if year else ""
    query = text(base_query.format(where=where))
    params = {"year": year} if year else {}
    rows = db.execute(query, params).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Monthly revenue trend fetched successfully",
        data=data,
        total_records=len(data),
    )


@router.get("/by-category", response_model=APIResponse)
def get_revenue_by_category(db: Session = Depends(get_db)):
    """Revenue and profit grouped by business category."""
    query = text("""
        SELECT
            b.business_category,
            COUNT(DISTINCT cam.business_id)               AS total_businesses,
            COUNT(cam.campaign_id)                        AS total_campaigns,
            ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
            ROUND(SUM(cam.profit_generated)::NUMERIC, 2)  AS total_profit,
            ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
            ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas
        FROM campaigns cam
        JOIN businesses b ON cam.business_id = b.business_id
        GROUP BY b.business_category
        ORDER BY total_profit DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Revenue by category fetched successfully",
        data=data,
        total_records=len(data),
    )


@router.get("/by-season", response_model=APIResponse)
def get_revenue_by_season(db: Session = Depends(get_db)):
    """Revenue performance broken down by season."""
    query = text("""
        SELECT
            season,
            COUNT(campaign_id)                           AS total_campaigns,
            ROUND(SUM(ad_spend)::NUMERIC, 2)             AS total_ad_spend,
            ROUND(SUM(revenue_generated)::NUMERIC, 2)    AS total_revenue,
            ROUND(SUM(profit_generated)::NUMERIC, 2)     AS total_profit,
            ROUND(AVG(roas)::NUMERIC, 4)                 AS avg_roas
        FROM campaigns
        GROUP BY season
        ORDER BY total_revenue DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Revenue by season fetched successfully",
        data=data,
        total_records=len(data),
    )


@router.get("/top-campaigns", response_model=APIResponse)
def get_top_campaigns(
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db),
):
    """Top campaigns ranked by ROI."""
    query = text("""
        SELECT
            cam.campaign_id,
            b.business_name,
            b.business_category,
            cam.platform,
            cam.campaign_type,
            cam.season,
            ROUND(cam.ad_spend::NUMERIC, 2)           AS ad_spend,
            ROUND(cam.revenue_generated::NUMERIC, 2)  AS revenue,
            ROUND(cam.profit_generated::NUMERIC, 2)   AS profit,
            ROUND(cam.roi::NUMERIC, 4)                AS roi,
            ROUND(cam.roas::NUMERIC, 4)               AS roas
        FROM campaigns cam
        JOIN businesses b ON cam.business_id = b.business_id
        ORDER BY cam.roi DESC
        LIMIT :limit
    """)
    rows = db.execute(query, {"limit": limit}).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message=f"Top {limit} campaigns by ROI fetched successfully",
        data=data,
        total_records=len(data),
    )


# Fix missing import
from typing import Optional