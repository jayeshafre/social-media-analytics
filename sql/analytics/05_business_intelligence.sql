-- ============================================================
-- FILE    : 05_business_intelligence.sql
-- PURPOSE : Advanced BI — CAC, Funnels, Cohorts
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- Q19. Customer Acquisition Cost (CAC) by Platform
--      Formula: CAC = Total Ad Spend / Total New Customers
-- ─────────────────────────────────────────────────────────────
SELECT
    cam.platform,
    ROUND(SUM(cam.ad_spend)::NUMERIC, 2)       AS total_ad_spend,
    COUNT(cv.conversion_id)                    AS total_conversions,
    COUNT(CASE WHEN cv.repeat_customer = FALSE
               THEN 1 END)                     AS new_customers,
    ROUND(
        SUM(cam.ad_spend) /
        NULLIF(COUNT(CASE WHEN cv.repeat_customer = FALSE
                          THEN 1 END), 0)
    ::NUMERIC, 2)                              AS cac
FROM campaigns cam
LEFT JOIN conversions cv ON cam.campaign_id = cv.campaign_id
GROUP BY cam.platform
ORDER BY cac ASC;


-- ─────────────────────────────────────────────────────────────
-- Q20. Conversion Funnel: Impressions → Clicks → Conversions
-- ─────────────────────────────────────────────────────────────
SELECT
    platform,
    SUM(impressions)                           AS total_impressions,
    SUM(clicks)                                AS total_clicks,
    SUM(conversions)                           AS total_conversions,
    ROUND(
        SUM(clicks) * 100.0 / NULLIF(SUM(impressions), 0)
    ::NUMERIC, 4)                              AS impression_to_click_pct,
    ROUND(
        SUM(conversions) * 100.0 / NULLIF(SUM(clicks), 0)
    ::NUMERIC, 4)                              AS click_to_conversion_pct,
    ROUND(
        SUM(conversions) * 100.0 / NULLIF(SUM(impressions), 0)
    ::NUMERIC, 6)                              AS overall_funnel_pct
FROM campaigns
GROUP BY platform
ORDER BY overall_funnel_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- Q21. Payment Method Preference by Platform
-- ─────────────────────────────────────────────────────────────
SELECT
    cam.platform,
    cv.payment_method,
    COUNT(cv.conversion_id)                   AS total_conversions,
    ROUND(SUM(cv.order_value)::NUMERIC, 2)    AS total_revenue,
    ROUND(AVG(cv.order_value)::NUMERIC, 2)    AS avg_order_value
FROM conversions cv
JOIN campaigns cam ON cv.campaign_id = cam.campaign_id
GROUP BY cam.platform, cv.payment_method
ORDER BY cam.platform, total_conversions DESC;


-- ─────────────────────────────────────────────────────────────
-- Q22. Repeat vs New Customer Revenue Split
-- ─────────────────────────────────────────────────────────────
SELECT
    repeat_customer,
    COUNT(conversion_id)                      AS total_conversions,
    ROUND(SUM(order_value)::NUMERIC, 2)       AS total_revenue,
    ROUND(AVG(order_value)::NUMERIC, 2)       AS avg_order_value,
    ROUND(SUM(profit_amount)::NUMERIC, 2)     AS total_profit,
    ROUND(AVG(discount_pct)::NUMERIC, 1)      AS avg_discount_pct
FROM conversions
GROUP BY repeat_customer;


-- ─────────────────────────────────────────────────────────────
-- Q23. Refund Impact Analysis
-- ─────────────────────────────────────────────────────────────
SELECT
    refund_status,
    COUNT(conversion_id)                      AS total_conversions,
    ROUND(SUM(order_value)::NUMERIC, 2)       AS gross_revenue,
    ROUND(SUM(profit_amount)::NUMERIC, 2)     AS gross_profit,
    ROUND(AVG(order_value)::NUMERIC, 2)       AS avg_order_value,
    ROUND(
        COUNT(conversion_id) * 100.0 /
        SUM(COUNT(conversion_id)) OVER ()
    ::NUMERIC, 2)                             AS pct_of_total
FROM conversions
GROUP BY refund_status
ORDER BY total_conversions DESC;


-- ─────────────────────────────────────────────────────────────
-- Q24. Year-over-Year Revenue Growth (Window Function)
-- ─────────────────────────────────────────────────────────────
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
    LAG(annual_revenue) OVER (ORDER BY year)   AS prev_year_revenue,
    ROUND(
        (annual_revenue - LAG(annual_revenue) OVER (ORDER BY year))
        * 100.0
        / NULLIF(LAG(annual_revenue) OVER (ORDER BY year), 0)
    ::NUMERIC, 2)                              AS yoy_growth_pct
FROM yearly
ORDER BY year;