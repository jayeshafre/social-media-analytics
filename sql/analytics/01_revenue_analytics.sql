-- ============================================================
-- FILE    : 01_revenue_analytics.sql
-- PURPOSE : Revenue & Profitability Analytics
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- Q1. Total Revenue, Profit & ROAS by Platform
--     Business Question: Which platform generates the most revenue?
-- ─────────────────────────────────────────────────────────────
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
ORDER BY total_revenue DESC;


-- ─────────────────────────────────────────────────────────────
-- Q2. Monthly Revenue Trend (All Platforms Combined)
--     Business Question: How has revenue trended month over month?
-- ─────────────────────────────────────────────────────────────
SELECT
    c.year,
    c.month,
    c.month_name,
    c.quarter,
    ROUND(SUM(cam.revenue_generated)::NUMERIC, 2)  AS monthly_revenue,
    ROUND(SUM(cam.profit_generated)::NUMERIC, 2)   AS monthly_profit,
    ROUND(SUM(cam.ad_spend)::NUMERIC, 2)           AS monthly_ad_spend,
    COUNT(cam.campaign_id)                         AS campaigns_run
FROM campaigns cam
JOIN calendar c ON cam.start_date = c.date
GROUP BY c.year, c.month, c.month_name, c.quarter
ORDER BY c.year, c.month;


-- ─────────────────────────────────────────────────────────────
-- Q3. Revenue by Business Category
--     Business Question: Which category is most profitable?
-- ─────────────────────────────────────────────────────────────
SELECT
    b.business_category,
    COUNT(DISTINCT cam.business_id)              AS total_businesses,
    COUNT(cam.campaign_id)                       AS total_campaigns,
    ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS total_revenue,
    ROUND(SUM(cam.profit_generated)::NUMERIC, 2)  AS total_profit,
    ROUND(AVG(cam.roi)::NUMERIC, 4)               AS avg_roi,
    ROUND(AVG(cam.roas)::NUMERIC, 4)              AS avg_roas
FROM campaigns cam
JOIN businesses b ON cam.business_id = b.business_id
GROUP BY b.business_category
ORDER BY total_profit DESC;


-- ─────────────────────────────────────────────────────────────
-- Q4. Top 10 Campaigns by ROI
--     Business Question: Which campaigns delivered the best ROI?
-- ─────────────────────────────────────────────────────────────
SELECT
    cam.campaign_id,
    b.business_name,
    b.business_category,
    cam.platform,
    cam.campaign_type,
    cam.season,
    ROUND(cam.ad_spend::NUMERIC, 2)            AS ad_spend,
    ROUND(cam.revenue_generated::NUMERIC, 2)   AS revenue,
    ROUND(cam.profit_generated::NUMERIC, 2)    AS profit,
    ROUND(cam.roi::NUMERIC, 4)                 AS roi,
    ROUND(cam.roas::NUMERIC, 4)                AS roas
FROM campaigns cam
JOIN businesses b ON cam.business_id = b.business_id
ORDER BY cam.roi DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- Q5. Revenue by Season
--     Business Question: Which season drives the most revenue?
-- ─────────────────────────────────────────────────────────────
SELECT
    season,
    COUNT(campaign_id)                           AS total_campaigns,
    ROUND(SUM(ad_spend)::NUMERIC, 2)             AS total_ad_spend,
    ROUND(SUM(revenue_generated)::NUMERIC, 2)    AS total_revenue,
    ROUND(SUM(profit_generated)::NUMERIC, 2)     AS total_profit,
    ROUND(AVG(roas)::NUMERIC, 4)                 AS avg_roas
FROM campaigns
GROUP BY season
ORDER BY total_revenue DESC;


-- ─────────────────────────────────────────────────────────────
-- Q6. Running Revenue Total by Month (Window Function)
--     Business Question: What is our cumulative revenue growth?
-- ─────────────────────────────────────────────────────────────
WITH monthly AS (
    SELECT
        c.year,
        c.month,
        c.month_name,
        ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS monthly_revenue
    FROM campaigns cam
    JOIN calendar c ON cam.start_date = c.date
    GROUP BY c.year, c.month, c.month_name
)
SELECT
    year,
    month,
    month_name,
    monthly_revenue,
    ROUND(
        SUM(monthly_revenue) OVER (
            PARTITION BY year
            ORDER BY month
        )::NUMERIC, 2
    ) AS cumulative_revenue_ytd
FROM monthly
ORDER BY year, month;