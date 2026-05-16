"""
Engagement Analytics Endpoints
Exposes the 1.1M row engagement_metrics table — previously unused.
Covers sentiment trends, video performance, and snapshot progression.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.schemas.responses import APIResponse
from typing import Optional

router = APIRouter(prefix="/engagement", tags=["Engagement Analytics"])


@router.get("/sentiment-by-platform", response_model=APIResponse)
def get_sentiment_by_platform(db: Session = Depends(get_db)):
    """
    Average sentiment score per platform across all engagement snapshots.
    Sentiment score: 0.0 (negative) → 1.0 (positive).
    Useful for brand health monitoring.
    """
    query = text("""
        SELECT
            c.platform,
            COUNT(e.engagement_id)                    AS total_snapshots,
            ROUND(AVG(e.sentiment_score)::NUMERIC, 3) AS avg_sentiment,
            ROUND(MIN(e.sentiment_score)::NUMERIC, 3) AS min_sentiment,
            ROUND(MAX(e.sentiment_score)::NUMERIC, 3) AS max_sentiment,
            ROUND(AVG(e.engagement_rate)::NUMERIC, 5) AS avg_engagement_rate
        FROM engagement_metrics e
        JOIN campaigns c ON e.campaign_id = c.campaign_id
        GROUP BY c.platform
        ORDER BY avg_sentiment DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Sentiment by platform fetched successfully",
        data=data,
        total_records=len(data),
    )


@router.get("/video-performance", response_model=APIResponse)
def get_video_performance(
    platform: Optional[str] = Query(
        None, description="Filter: Instagram or YouTube"
    ),
    db: Session = Depends(get_db),
):
    """
    Video views and watch time analytics.
    Only Instagram and YouTube have meaningful video_views data.
    Other platforms return 0 for video_views by design.
    """
    base = """
        SELECT
            c.platform,
            c.campaign_type,
            COUNT(e.engagement_id)                           AS total_snapshots,
            SUM(e.video_views)                               AS total_video_views,
            ROUND(AVG(e.video_views)::NUMERIC, 0)            AS avg_video_views,
            SUM(e.watch_time_seconds)                        AS total_watch_seconds,
            ROUND(
                SUM(e.watch_time_seconds) / 3600.0
            ::NUMERIC, 1)                                    AS total_watch_hours,
            ROUND(AVG(e.engagement_rate)::NUMERIC, 5)        AS avg_engagement_rate,
            ROUND(AVG(e.sentiment_score)::NUMERIC, 3)        AS avg_sentiment
        FROM engagement_metrics e
        JOIN campaigns c ON e.campaign_id = c.campaign_id
        WHERE e.video_views > 0
        {where}
        GROUP BY c.platform, c.campaign_type
        ORDER BY total_video_views DESC
    """
    where = "AND c.platform = :platform" if platform else ""
    query = text(base.format(where=where))
    params = {"platform": platform} if platform else {}
    rows = db.execute(query, params).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Video performance fetched successfully",
        data=data,
        total_records=len(data),
    )


@router.get("/engagement-progression", response_model=APIResponse)
def get_engagement_progression(db: Session = Depends(get_db)):
    """
    How engagement metrics grow across campaign snapshots (1→7).
    Shows whether campaigns build momentum over time.
    """
    query = text("""
        SELECT
            snapshot_number,
            COUNT(engagement_id)                      AS total_snapshots,
            ROUND(AVG(likes)::NUMERIC, 0)             AS avg_likes,
            ROUND(AVG(comments)::NUMERIC, 0)          AS avg_comments,
            ROUND(AVG(shares)::NUMERIC, 0)            AS avg_shares,
            ROUND(AVG(saves)::NUMERIC, 0)             AS avg_saves,
            ROUND(AVG(engagement_rate)::NUMERIC, 5)   AS avg_engagement_rate,
            ROUND(AVG(sentiment_score)::NUMERIC, 3)   AS avg_sentiment
        FROM engagement_metrics
        GROUP BY snapshot_number
        ORDER BY snapshot_number
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message="Engagement progression fetched successfully",
        data=data,
        total_records=len(data),
    )


@router.get("/top-by-sentiment", response_model=APIResponse)
def get_top_campaigns_by_sentiment(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Top campaigns ranked by average audience sentiment score.
    High sentiment = positive audience reaction to the ad.
    """
    query = text("""
        SELECT
            e.campaign_id,
            c.platform,
            c.campaign_type,
            c.campaign_objective,
            b.business_name,
            b.business_category,
            COUNT(e.engagement_id)                    AS total_snapshots,
            ROUND(AVG(e.sentiment_score)::NUMERIC, 3) AS avg_sentiment,
            ROUND(AVG(e.engagement_rate)::NUMERIC, 5) AS avg_engagement_rate,
            ROUND(c.roas::NUMERIC, 4)                 AS roas
        FROM engagement_metrics e
        JOIN campaigns  c ON e.campaign_id  = c.campaign_id
        JOIN businesses b ON c.business_id  = b.business_id
        GROUP BY
            e.campaign_id, c.platform, c.campaign_type,
            c.campaign_objective, b.business_name,
            b.business_category, c.roas
        ORDER BY avg_sentiment DESC
        LIMIT :limit
    """)
    rows = db.execute(query, {"limit": limit}).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message=f"Top {limit} campaigns by sentiment fetched",
        data=data,
        total_records=len(data),
    )


@router.get("/by-campaign/{campaign_id}", response_model=APIResponse)
def get_engagement_for_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
):
    """
    All engagement snapshots for a specific campaign.
    Shows the full engagement timeline from snapshot 1 → 7.
    """
    query = text("""
        SELECT
            engagement_id,
            snapshot_number,
            likes,
            comments,
            shares,
            saves,
            video_views,
            watch_time_seconds,
            ROUND(engagement_rate::NUMERIC, 5) AS engagement_rate,
            ROUND(sentiment_score::NUMERIC, 3) AS sentiment_score
        FROM engagement_metrics
        WHERE campaign_id = :campaign_id
        ORDER BY snapshot_number
    """)
    rows = db.execute(query, {"campaign_id": campaign_id}).mappings().all()
    if not rows:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"No engagement data for campaign {campaign_id}"
        )
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True,
        message=f"Engagement snapshots for {campaign_id} fetched",
        data=data,
        total_records=len(data),
    )