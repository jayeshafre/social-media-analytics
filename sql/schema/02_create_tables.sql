-- ============================================================
-- Script  : 02_create_tables.sql
-- Project : Multi-Platform Social Media Analytics
-- Purpose : Create all dimension and fact tables
-- Schema  : Star Schema
-- ============================================================


-- ─────────────────────────────────────────────
-- DIMENSION TABLE 1: platforms
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS platforms (
    platform_id             VARCHAR(10)     PRIMARY KEY,
    platform_name           VARCHAR(50)     NOT NULL UNIQUE,
    platform_type           VARCHAR(30)     NOT NULL,
    avg_market_ctr          NUMERIC(6,4)    NOT NULL,
    avg_market_cpc          NUMERIC(8,2)    NOT NULL,
    audience_type           VARCHAR(50),
    primary_use_case        VARCHAR(100),
    monthly_active_users_m  INTEGER,
    primary_content_format  VARCHAR(100),
    b2b_suitability         VARCHAR(10),
    launched_year           INTEGER
);


-- ─────────────────────────────────────────────
-- DIMENSION TABLE 2: calendar
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS calendar (
    date                DATE            PRIMARY KEY,
    day_of_week         VARCHAR(15)     NOT NULL,
    day_of_month        SMALLINT        NOT NULL,
    week_of_year        SMALLINT        NOT NULL,
    month               SMALLINT        NOT NULL,
    month_name          VARCHAR(15)     NOT NULL,
    quarter             VARCHAR(5)      NOT NULL,
    year                SMALLINT        NOT NULL,
    is_weekend          BOOLEAN         NOT NULL DEFAULT FALSE,
    festival_season     VARCHAR(30),
    sales_event         VARCHAR(50)     DEFAULT 'No Event',
    financial_year      VARCHAR(15)
);


-- ─────────────────────────────────────────────
-- DIMENSION TABLE 3: businesses
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS businesses (
    business_id             VARCHAR(10)     PRIMARY KEY,
    business_name           VARCHAR(150)    NOT NULL,
    business_category       VARCHAR(50)     NOT NULL,
    business_type           VARCHAR(10)     NOT NULL,
    city                    VARCHAR(50),
    country                 VARCHAR(50),
    target_audience         VARCHAR(50),
    avg_profit_margin       NUMERIC(5,4),
    annual_revenue_band     VARCHAR(20),
    founded_year            INTEGER,
    is_influencer_brand     BOOLEAN         DEFAULT FALSE,
    primary_platform        VARCHAR(50),
    employee_count_band     VARCHAR(20)
);


-- ─────────────────────────────────────────────
-- DIMENSION TABLE 4: customers
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customers (
    customer_id             VARCHAR(15)     PRIMARY KEY,
    age_group               VARCHAR(10)     NOT NULL,
    gender                  VARCHAR(10)     NOT NULL,
    location                VARCHAR(50),
    income_level            VARCHAR(20),
    interests               TEXT,
    preferred_platform      VARCHAR(50),
    avg_purchase_value      NUMERIC(10,2),
    engagement_level        VARCHAR(15),
    loyalty_segment         VARCHAR(15),
    is_mobile_first         BOOLEAN         DEFAULT TRUE,
    customer_since_year     SMALLINT
);


-- ─────────────────────────────────────────────
-- FACT TABLE 1: campaigns  ← CORE TABLE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id             VARCHAR(12)     PRIMARY KEY,
    business_id             VARCHAR(10)     NOT NULL,
    platform                VARCHAR(50)     NOT NULL,
    campaign_objective      VARCHAR(50),
    campaign_type           VARCHAR(30),
    start_date              DATE,
    end_date                DATE,
    duration_days           SMALLINT,
    campaign_stage          VARCHAR(20),
    season                  VARCHAR(30),
    ad_spend                NUMERIC(12,2),
    impressions             INTEGER,
    clicks                  INTEGER,
    ctr                     NUMERIC(8,5),
    cpc                     NUMERIC(8,2),
    conversions             INTEGER,
    conversion_rate         NUMERIC(8,5),
    revenue_generated       NUMERIC(14,2),
    profit_generated        NUMERIC(14,2),
    roas                    NUMERIC(10,4),
    roi                     NUMERIC(10,4),
    engagement_rate         NUMERIC(8,5),
    likes                   INTEGER,
    comments                INTEGER,
    shares                  INTEGER,
    saves                   INTEGER,
    audience_age_group      VARCHAR(10),
    audience_gender         VARCHAR(10),
    device_type             VARCHAR(15),
    influencer_used         BOOLEAN         DEFAULT FALSE,
    sentiment_score         NUMERIC(4,3),

    -- Foreign Keys
    CONSTRAINT fk_campaign_business
        FOREIGN KEY (business_id)
        REFERENCES businesses(business_id),

    CONSTRAINT fk_campaign_platform
        FOREIGN KEY (platform)
        REFERENCES platforms(platform_name),

    CONSTRAINT fk_campaign_date
        FOREIGN KEY (start_date)
        REFERENCES calendar(date)
);


-- ─────────────────────────────────────────────
-- FACT TABLE 2: engagement_metrics
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS engagement_metrics (
    engagement_id           VARCHAR(12)     PRIMARY KEY,
    campaign_id             VARCHAR(12)     NOT NULL,
    snapshot_number         SMALLINT        NOT NULL,
    likes                   INTEGER,
    comments                INTEGER,
    shares                  INTEGER,
    saves                   INTEGER,
    video_views             INTEGER,
    watch_time_seconds      BIGINT,
    engagement_rate         NUMERIC(8,5),
    sentiment_score         NUMERIC(4,3),

    -- Foreign Key
    CONSTRAINT fk_engagement_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES campaigns(campaign_id)
);


-- ─────────────────────────────────────────────
-- FACT TABLE 3: conversions
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversions (
    conversion_id           VARCHAR(12)     PRIMARY KEY,
    campaign_id             VARCHAR(12)     NOT NULL,
    customer_id             VARCHAR(15)     NOT NULL,
    conversion_date         DATE,
    order_value             NUMERIC(12,2),
    discount_used           BOOLEAN         DEFAULT FALSE,
    discount_pct            SMALLINT        DEFAULT 0,
    payment_method          VARCHAR(20),
    repeat_customer         BOOLEAN         DEFAULT FALSE,
    refund_status           VARCHAR(20),
    profit_amount           NUMERIC(12,2),
    conversion_type         VARCHAR(20),
    attribution_model       VARCHAR(20),

    -- Foreign Keys
    CONSTRAINT fk_conversion_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES campaigns(campaign_id),

    CONSTRAINT fk_conversion_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_conversion_date
        FOREIGN KEY (conversion_date)
        REFERENCES calendar(date)
);