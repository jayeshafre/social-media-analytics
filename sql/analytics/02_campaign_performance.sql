-- ============================================================
-- FILE    : 02_campaign_performance.sql
-- PURPOSE : Campaign Performance Analytics
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- Q7. CTR by Campaign Type per Platform
--     Business Question: Which ad format works best per platform?
-- ─────────────────────────────────────────────────────────────
SELECT
    platform,
    campaign_type,
    COUNT(campaign_id)             AS total_campaigns,
    ROUND(AVG(ctr)::NUMERIC, 5)    AS avg_ctr,
    ROUND(AVG(cpc)::NUMERIC, 2)    AS avg_cpc,
    ROUND(AVG(roas)::NUMERIC, 4)   AS avg_roas,
    ROUND(AVG(roi)::NUMERIC, 4)    AS avg_roi
FROM campaigns
GROUP BY platform, campaign_type
ORDER BY platform, avg_ctr DESC;


-- ─────────────────────────────────────────────────────────────
-- Q8. Conversion Rate by Campaign Objective
--     Business Question: Which objective has best conversion rate?
-- ─────────────────────────────────────────────────────────────
SELECT
    campaign_objective,
    COUNT(campaign_id)                       AS total_campaigns,
    ROUND(AVG(conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
    ROUND(AVG(cpc)::NUMERIC, 2)              AS avg_cpc,
    ROUND(AVG(roas)::NUMERIC, 4)             AS avg_roas,
    SUM(conversions)                         AS total_conversions
FROM campaigns
GROUP BY campaign_objective
ORDER BY avg_conversion_rate DESC;


-- ─────────────────────────────────────────────────────────────
-- Q9. Campaign Duration vs Performance
--     Business Question: Do longer campaigns perform better?
-- ─────────────────────────────────────────────────────────────
SELECT
    campaign_stage,
    COUNT(campaign_id)                       AS total_campaigns,
    ROUND(AVG(duration_days)::NUMERIC, 1)    AS avg_duration_days,
    ROUND(AVG(roas)::NUMERIC, 4)             AS avg_roas,
    ROUND(AVG(roi)::NUMERIC, 4)              AS avg_roi,
    ROUND(AVG(conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
    ROUND(AVG(ctr)::NUMERIC, 5)              AS avg_ctr
FROM campaigns
GROUP BY campaign_stage
ORDER BY avg_roas DESC;


-- ─────────────────────────────────────────────────────────────
-- Q10. Influencer vs Non-Influencer Campaign Performance
--      Business Question: Do influencer campaigns outperform?
-- ─────────────────────────────────────────────────────────────
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
GROUP BY influencer_used;


-- ─────────────────────────────────────────────────────────────
-- Q11. Campaign Performance Ranking Within Each Platform
--      (Window Function — RANK)
-- ─────────────────────────────────────────────────────────────
WITH ranked AS (
    SELECT
        campaign_id,
        platform,
        campaign_type,
        ROUND(revenue_generated::NUMERIC, 2)  AS revenue,
        ROUND(roi::NUMERIC, 4)                AS roi,
        RANK() OVER (
            PARTITION BY platform
            ORDER BY roi DESC
        ) AS rank_within_platform
    FROM campaigns
)
SELECT *
FROM ranked
WHERE rank_within_platform <= 5
ORDER BY platform, rank_within_platform;