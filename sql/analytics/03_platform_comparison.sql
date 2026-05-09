-- ============================================================
-- FILE    : 03_platform_comparison.sql
-- PURPOSE : Cross-Platform Benchmarking
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- Q12. Platform Performance vs Market Benchmark
--      Business Question: Are our campaigns beating market CTR?
-- ─────────────────────────────────────────────────────────────
SELECT
    cam.platform,
    p.avg_market_ctr                              AS market_benchmark_ctr,
    ROUND(AVG(cam.ctr)::NUMERIC, 5)               AS our_avg_ctr,
    ROUND(
        (AVG(cam.ctr) - p.avg_market_ctr)::NUMERIC
        / p.avg_market_ctr * 100, 2
    )                                             AS ctr_vs_benchmark_pct,
    p.avg_market_cpc                              AS market_benchmark_cpc,
    ROUND(AVG(cam.cpc)::NUMERIC, 2)               AS our_avg_cpc,
    ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas,
    COUNT(cam.campaign_id)                        AS total_campaigns
FROM campaigns cam
JOIN platforms p ON cam.platform = p.platform_name
GROUP BY cam.platform, p.avg_market_ctr, p.avg_market_cpc
ORDER BY ctr_vs_benchmark_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- Q13. Best Platform per Business Category
--      Business Question: Where should each category advertise?
-- ─────────────────────────────────────────────────────────────
WITH category_platform AS (
    SELECT
        b.business_category,
        cam.platform,
        ROUND(AVG(cam.roi)::NUMERIC, 4)   AS avg_roi,
        ROUND(AVG(cam.roas)::NUMERIC, 4)  AS avg_roas,
        COUNT(cam.campaign_id)            AS campaigns,
        RANK() OVER (
            PARTITION BY b.business_category
            ORDER BY AVG(cam.roi) DESC
        ) AS platform_rank
    FROM campaigns cam
    JOIN businesses b ON cam.business_id = b.business_id
    GROUP BY b.business_category, cam.platform
)
SELECT
    business_category,
    platform         AS best_platform,
    avg_roi,
    avg_roas,
    campaigns
FROM category_platform
WHERE platform_rank = 1
ORDER BY avg_roi DESC;


-- ─────────────────────────────────────────────────────────────
-- Q14. Platform Share of Total Ad Spend and Revenue
-- ─────────────────────────────────────────────────────────────
SELECT
    platform,
    ROUND(SUM(ad_spend)::NUMERIC, 2)          AS total_spend,
    ROUND(
        SUM(ad_spend) * 100.0 /
        SUM(SUM(ad_spend)) OVER ()
    ::NUMERIC, 2)                             AS spend_share_pct,
    ROUND(SUM(revenue_generated)::NUMERIC, 2) AS total_revenue,
    ROUND(
        SUM(revenue_generated) * 100.0 /
        SUM(SUM(revenue_generated)) OVER ()
    ::NUMERIC, 2)                             AS revenue_share_pct
FROM campaigns
GROUP BY platform
ORDER BY total_revenue DESC;