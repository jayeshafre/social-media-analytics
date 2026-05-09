-- ============================================================
-- FILE    : 04_audience_insights.sql
-- PURPOSE : Audience Demographics & Behaviour Analytics
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- Q15. Conversion Rate by Age Group
--      Business Question: Which age group converts the most?
-- ─────────────────────────────────────────────────────────────
SELECT
    audience_age_group,
    COUNT(campaign_id)                       AS total_campaigns,
    SUM(conversions)                         AS total_conversions,
    ROUND(AVG(conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
    ROUND(AVG(ctr)::NUMERIC, 5)              AS avg_ctr,
    ROUND(AVG(roas)::NUMERIC, 4)             AS avg_roas
FROM campaigns
GROUP BY audience_age_group
ORDER BY avg_conversion_rate DESC;


-- ─────────────────────────────────────────────────────────────
-- Q16. Device Type Performance
--      Business Question: Mobile vs Desktop — which converts better?
-- ─────────────────────────────────────────────────────────────
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
ORDER BY avg_conversion_rate DESC;


-- ─────────────────────────────────────────────────────────────
-- Q17. Gender Targeting Performance
-- ─────────────────────────────────────────────────────────────
SELECT
    audience_gender,
    COUNT(campaign_id)                       AS total_campaigns,
    ROUND(AVG(ctr)::NUMERIC, 5)              AS avg_ctr,
    ROUND(AVG(conversion_rate)::NUMERIC, 5)  AS avg_conversion_rate,
    ROUND(AVG(roas)::NUMERIC, 4)             AS avg_roas,
    ROUND(SUM(revenue_generated)::NUMERIC, 2) AS total_revenue
FROM campaigns
GROUP BY audience_gender
ORDER BY avg_roas DESC;


-- ─────────────────────────────────────────────────────────────
-- Q18. Customer Order Value by Income Level
--      (Using conversions + customers join)
-- ─────────────────────────────────────────────────────────────
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
ORDER BY avg_order_value DESC;