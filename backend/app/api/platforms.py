"""Platform Comparison Endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/platforms", tags=["Platform Comparison"])


@router.get("/overview", response_model=APIResponse)
def get_platform_overview(db: Session = Depends(get_db)):
    """All platform metadata from dimension table."""
    query = text("SELECT * FROM platforms ORDER BY monthly_active_users_m DESC")
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Platform overview fetched",
        data=data, total_records=len(data),
    )


@router.get("/vs-benchmark", response_model=APIResponse)
def get_vs_benchmark(db: Session = Depends(get_db)):
    """Our CTR/CPC vs industry market benchmarks per platform."""
    query = text("""
        SELECT
            cam.platform,
            p.avg_market_ctr,
            ROUND(AVG(cam.ctr)::NUMERIC, 5)             AS our_avg_ctr,
            ROUND((AVG(cam.ctr) - p.avg_market_ctr)
                / p.avg_market_ctr * 100::NUMERIC, 2)   AS ctr_vs_benchmark_pct,
            p.avg_market_cpc,
            ROUND(AVG(cam.cpc)::NUMERIC, 2)             AS our_avg_cpc,
            ROUND(AVG(cam.roas)::NUMERIC, 4)            AS avg_roas,
            COUNT(cam.campaign_id)                      AS total_campaigns
        FROM campaigns cam
        JOIN platforms p ON cam.platform = p.platform_name
        GROUP BY cam.platform, p.avg_market_ctr, p.avg_market_cpc
        ORDER BY ctr_vs_benchmark_pct DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Platform vs benchmark fetched",
        data=data, total_records=len(data),
    )


@router.get("/revenue-share", response_model=APIResponse)
def get_revenue_share(db: Session = Depends(get_db)):
    """Each platform's share of total ad spend and revenue."""
    query = text("""
        SELECT
            platform,
            ROUND(SUM(ad_spend)::NUMERIC, 2)           AS total_spend,
            ROUND(SUM(ad_spend) * 100.0
                / SUM(SUM(ad_spend)) OVER ()
            ::NUMERIC, 2)                              AS spend_share_pct,
            ROUND(SUM(revenue_generated)::NUMERIC, 2)  AS total_revenue,
            ROUND(SUM(revenue_generated) * 100.0
                / SUM(SUM(revenue_generated)) OVER ()
            ::NUMERIC, 2)                              AS revenue_share_pct
        FROM campaigns
        GROUP BY platform
        ORDER BY total_revenue DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Platform revenue share fetched",
        data=data, total_records=len(data),
    )


@router.get("/best-per-category", response_model=APIResponse)
def get_best_platform_per_category(db: Session = Depends(get_db)):
    """Best performing platform for each business category."""
    query = text("""
        WITH ranked AS (
            SELECT
                b.business_category,
                cam.platform,
                ROUND(AVG(cam.roi)::NUMERIC, 4)   AS avg_roi,
                ROUND(AVG(cam.roas)::NUMERIC, 4)  AS avg_roas,
                COUNT(cam.campaign_id)            AS campaigns,
                RANK() OVER (
                    PARTITION BY b.business_category
                    ORDER BY AVG(cam.roi) DESC
                ) AS rnk
            FROM campaigns cam
            JOIN businesses b ON cam.business_id = b.business_id
            GROUP BY b.business_category, cam.platform
        )
        SELECT business_category, platform AS best_platform,
               avg_roi, avg_roas, campaigns
        FROM ranked
        WHERE rnk = 1
        ORDER BY avg_roi DESC
    """)
    rows = db.execute(query).mappings().all()
    data = [dict(r) for r in rows]
    return APIResponse(
        success=True, message="Best platform per category fetched",
        data=data, total_records=len(data),
    )