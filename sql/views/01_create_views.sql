-- ============================================================
-- FILE    : 01_create_views.sql
-- PURPOSE : Create reusable views for dashboard & API layer
-- ============================================================


-- View 1: Executive Summary by Platform
CREATE OR REPLACE VIEW vw_executive_summary AS
SELECT
    platform,
    COUNT(campaign_id)                           AS total_campaigns,
    ROUND(SUM(ad_spend)::NUMERIC, 2)             AS total_ad_spend,
    ROUND(SUM(revenue_generated)::NUMERIC, 2)    AS total_revenue,
    ROUND(SUM(profit_generated)::NUMERIC, 2)     AS total_profit,
    ROUND(AVG(roas)::NUMERIC, 4)                 AS avg_roas,
    ROUND(AVG(roi)::NUMERIC, 4)                  AS avg_roi,
    ROUND(AVG(ctr)::NUMERIC, 5)                  AS avg_ctr,
    SUM(conversions)                             AS total_conversions
FROM campaigns
GROUP BY platform;


-- View 2: Monthly Revenue Dashboard
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    c.year,
    c.month,
    c.month_name,
    c.quarter,
    c.financial_year,
    ROUND(SUM(cam.revenue_generated)::NUMERIC, 2) AS monthly_revenue,
    ROUND(SUM(cam.profit_generated)::NUMERIC, 2)  AS monthly_profit,
    ROUND(SUM(cam.ad_spend)::NUMERIC, 2)          AS monthly_ad_spend,
    COUNT(cam.campaign_id)                        AS campaigns_run
FROM campaigns cam
JOIN calendar c ON cam.start_date = c.date
GROUP BY c.year, c.month, c.month_name, c.quarter, c.financial_year;


-- View 3: Campaign Full Detail (for API)
CREATE OR REPLACE VIEW vw_campaign_detail AS
SELECT
    cam.*,
    b.business_name,
    b.business_category,
    b.business_type,
    b.city,
    b.country
FROM campaigns cam
JOIN businesses b ON cam.business_id = b.business_id;


-- View 4: Conversion Detail (for API)
CREATE OR REPLACE VIEW vw_conversion_detail AS
SELECT
    cv.*,
    cu.age_group,
    cu.gender,
    cu.location,
    cu.income_level,
    cu.loyalty_segment,
    cam.platform,
    cam.campaign_objective
FROM conversions cv
JOIN customers  cu  ON cv.customer_id  = cu.customer_id
JOIN campaigns  cam ON cv.campaign_id  = cam.campaign_id;