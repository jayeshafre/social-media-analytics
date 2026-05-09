"""Campaign Performance Endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.schemas.responses import APIResponse
from typing import Optional

router = APIRouter(prefix="/campaigns", tags=["Campaign Analytics"])


@router.get("/performance-by-type", response_model=APIResponse)
def get_performance_by_type(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db),
):
    """CTR, CPC, ROAS by campaign type — optionally filtered by platform."""
    base = """
        SELECT
            platform,
            campaign_type,
            COUNT(campaign_id)             AS total_campaigns,
            ROUND(AVG(ctr)::NUMERIC, 5)    AS avg_ctr,
            ROUND(AVG(cpc)::NUMERIC, 2)    AS avg_cpc,
            ROUND(AVG(roas)::NUMERIC, 4)   AS avg_roas,
            ROUND(AVG(roi)::NUMERIC, 4)    AS avg_roi
        FROM campaigns
        {where}
        GROUP BY platform, campaign_type
        ORDER BY platform, avg_ctr DESC
    """
    where = "WHERE platform = :platform" if platform else ""
    query = text(base.format(where=where))
    params = {"platform": platform} if platform else {}
    rows = db.execute(query, params).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Campaign performance by type fetched",
        data=data,
        total_records=len(data),
    )


@router.get("/by-objective", response_model=APIResponse)
def get_by_objective(db: Session = Depends(get_db)):
    """Conversion rate and performance by campaign objective."""
    query = text("""
        SELECT
            campaign_objective,
            COUNT(campaign_id)                       AS total_campaigns,
            ROUND(AVG(conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
            ROUND(AVG(cpc)::NUMERIC, 2)              AS avg_cpc,
            ROUND(AVG(roas)::NUMERIC, 4)             AS avg_roas,
            SUM(conversions)                         AS total_conversions
        FROM campaigns
        GROUP BY campaign_objective
        ORDER BY avg_conversion_rate DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Campaign performance by objective fetched",
        data=data,
        total_records=len(data),
    )


@router.get("/influencer-impact", response_model=APIResponse)
def get_influencer_impact(db: Session = Depends(get_db)):
    """Influencer vs non-influencer campaign comparison."""
    query = text("""
        SELECT
            influencer_used,
            COUNT(campaign_id)                       AS total_campaigns,
            ROUND(AVG(ctr)::NUMERIC, 5)              AS avg_ctr,
            ROUND(AVG(conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
            ROUND(AVG(roas)::NUMERIC, 4)             AS avg_roas,
            ROUND(AVG(roi)::NUMERIC, 4)              AS avg_roi,
            ROUND(AVG(engagement_rate)::NUMERIC, 5)  AS avg_engagement_rate,
            ROUND(AVG(sentiment_score)::NUMERIC, 3)  AS avg_sentiment
        FROM campaigns
        GROUP BY influencer_used
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Influencer impact analysis fetched",
        data=data,
        total_records=len(data),
    )


@router.get("/{campaign_id}", response_model=APIResponse)
def get_campaign_detail(campaign_id: str, db: Session = Depends(get_db)):
    """Full detail for a single campaign by ID."""
    query = text("""
        SELECT
            cam.*,
            b.business_name,
            b.business_category,
            b.city,
            b.country
        FROM campaigns cam
        JOIN businesses b ON cam.business_id = b.business_id
        WHERE cam.campaign_id = :campaign_id
    """)
    row = db.execute(query, {"campaign_id": campaign_id}).mappings().first()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    return APIResponse(
        success=True,
        message="Campaign detail fetched",
        data=dict(row),
    )