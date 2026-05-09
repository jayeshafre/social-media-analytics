-- ============================================================
-- Script  : 03_create_indexes.sql
-- Purpose : Create indexes for query performance
-- ============================================================

-- campaigns indexes (most queried table)
CREATE INDEX IF NOT EXISTS idx_campaigns_platform
    ON campaigns(platform);

CREATE INDEX IF NOT EXISTS idx_campaigns_business_id
    ON campaigns(business_id);

CREATE INDEX IF NOT EXISTS idx_campaigns_start_date
    ON campaigns(start_date);

CREATE INDEX IF NOT EXISTS idx_campaigns_season
    ON campaigns(season);

CREATE INDEX IF NOT EXISTS idx_campaigns_objective
    ON campaigns(campaign_objective);

-- conversions indexes
CREATE INDEX IF NOT EXISTS idx_conversions_campaign_id
    ON conversions(campaign_id);

CREATE INDEX IF NOT EXISTS idx_conversions_customer_id
    ON conversions(customer_id);

CREATE INDEX IF NOT EXISTS idx_conversions_date
    ON conversions(conversion_date);

-- engagement indexes
CREATE INDEX IF NOT EXISTS idx_engagement_campaign_id
    ON engagement_metrics(campaign_id);

-- calendar indexes
CREATE INDEX IF NOT EXISTS idx_calendar_year
    ON calendar(year);

CREATE INDEX IF NOT EXISTS idx_calendar_month
    ON calendar(month);

CREATE INDEX IF NOT EXISTS idx_calendar_quarter
    ON calendar(quarter);