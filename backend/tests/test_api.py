"""
API Test Suite — Phase 10
Tests every router group with real DB connection.

Run with:
    cd backend
    pytest tests/ -v

Requirements:
    pip install pytest httpx
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ─────────────────────────────────────────
# HEALTH TESTS
# ─────────────────────────────────────────
class TestHealth:

    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_has_required_fields(self):
        data = client.get("/").json()
        assert "app" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_db_status(self):
        data = client.get("/health").json()
        assert "api" in data
        assert "database" in data
        assert data["api"] == "healthy"


# ─────────────────────────────────────────
# REVENUE TESTS
# ─────────────────────────────────────────
class TestRevenue:

    def test_revenue_by_platform_returns_200(self):
        response = client.get("/api/v1/revenue/by-platform")
        assert response.status_code == 200

    def test_revenue_by_platform_structure(self):
        data = client.get("/api/v1/revenue/by-platform").json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert data["total_records"] == 5         # 5 platforms

    def test_revenue_by_platform_fields(self):
        data = client.get("/api/v1/revenue/by-platform").json()
        row = data["data"][0]
        required = ["platform", "total_campaigns", "total_ad_spend",
                    "total_revenue", "total_profit", "avg_roas", "avg_roi"]
        for field in required:
            assert field in row, f"Missing field: {field}"

    def test_monthly_trend_no_filter(self):
        response = client.get("/api/v1/revenue/monthly-trend")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0

    def test_monthly_trend_with_year_filter(self):
        response = client.get("/api/v1/revenue/monthly-trend?year=2023")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 12        # 12 months in 2023

    def test_monthly_trend_invalid_year_returns_empty(self):
        response = client.get("/api/v1/revenue/monthly-trend?year=1900")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 0

    def test_revenue_by_category(self):
        response = client.get("/api/v1/revenue/by-category")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] > 0

    def test_revenue_by_season(self):
        response = client.get("/api/v1/revenue/by-season")
        assert response.status_code == 200

    def test_top_campaigns_default_limit(self):
        response = client.get("/api/v1/revenue/top-campaigns")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 10

    def test_top_campaigns_custom_limit(self):
        response = client.get("/api/v1/revenue/top-campaigns?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 5

    def test_top_campaigns_limit_too_high_rejected(self):
        response = client.get("/api/v1/revenue/top-campaigns?limit=999")
        assert response.status_code == 422          # FastAPI validation error


# ─────────────────────────────────────────
# CAMPAIGN TESTS
# ─────────────────────────────────────────
class TestCampaigns:

    def test_performance_by_type(self):
        response = client.get("/api/v1/campaigns/performance-by-type")
        assert response.status_code == 200

    def test_performance_by_type_with_platform_filter(self):
        response = client.get(
            "/api/v1/campaigns/performance-by-type?platform=Instagram"
        )
        assert response.status_code == 200
        data = response.json()
        for row in data["data"]:
            assert row["platform"] == "Instagram"

    def test_by_objective(self):
        response = client.get("/api/v1/campaigns/by-objective")
        assert response.status_code == 200

    def test_influencer_impact(self):
        response = client.get("/api/v1/campaigns/influencer-impact")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 2          # True / False

    def test_campaign_detail_valid_id(self):
        response = client.get("/api/v1/campaigns/CAM0000001")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["campaign_id"] == "CAM0000001"

    def test_campaign_detail_invalid_id_returns_404(self):
        response = client.get("/api/v1/campaigns/INVALID_ID")
        assert response.status_code == 404


# ─────────────────────────────────────────
# PLATFORM TESTS
# ─────────────────────────────────────────
class TestPlatforms:

    def test_overview_returns_5_platforms(self):
        response = client.get("/api/v1/platforms/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 5

    def test_vs_benchmark(self):
        response = client.get("/api/v1/platforms/vs-benchmark")
        assert response.status_code == 200

    def test_revenue_share(self):
        response = client.get("/api/v1/platforms/revenue-share")
        assert response.status_code == 200

    def test_best_per_category(self):
        response = client.get("/api/v1/platforms/best-per-category")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] > 0


# ─────────────────────────────────────────
# AUDIENCE TESTS
# ─────────────────────────────────────────
class TestAudience:

    def test_by_age_group(self):
        response = client.get("/api/v1/audience/by-age-group")
        assert response.status_code == 200

    def test_by_device(self):
        response = client.get("/api/v1/audience/by-device")
        assert response.status_code == 200
        data = response.json()
        devices = [r["device_type"] for r in data["data"]]
        assert "Mobile" in devices

    def test_by_income_level(self):
        response = client.get("/api/v1/audience/by-income-level")
        assert response.status_code == 200

    def test_by_gender(self):
        response = client.get("/api/v1/audience/by-gender")
        assert response.status_code == 200


# ─────────────────────────────────────────
# INTELLIGENCE TESTS
# ─────────────────────────────────────────
class TestIntelligence:

    def test_cac_by_platform(self):
        response = client.get("/api/v1/intelligence/cac-by-platform")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 5

    def test_conversion_funnel(self):
        response = client.get("/api/v1/intelligence/conversion-funnel")
        assert response.status_code == 200
        data = response.json()
        row = data["data"][0]
        assert "total_impressions" in row
        assert "total_clicks" in row
        assert "total_conversions" in row

    def test_yoy_growth(self):
        response = client.get("/api/v1/intelligence/yoy-growth")
        assert response.status_code == 200
        data = response.json()
        years = [r["year"] for r in data["data"]]
        assert 2019 in years
        assert 2024 in years

    def test_refund_analysis(self):
        response = client.get("/api/v1/intelligence/refund-analysis")
        assert response.status_code == 200
        data = response.json()
        statuses = [r["refund_status"] for r in data["data"]]
        assert "No Refund" in statuses


# ─────────────────────────────────────────
# ENGAGEMENT TESTS
# ─────────────────────────────────────────
class TestEngagement:

    def test_sentiment_by_platform(self):
        response = client.get("/api/v1/engagement/sentiment-by-platform")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 5
        row = data["data"][0]
        assert "avg_sentiment" in row
        assert 0 <= float(row["avg_sentiment"]) <= 1.0

    def test_video_performance(self):
        response = client.get("/api/v1/engagement/video-performance")
        assert response.status_code == 200

    def test_video_performance_platform_filter(self):
        response = client.get(
            "/api/v1/engagement/video-performance?platform=YouTube"
        )
        assert response.status_code == 200
        data = response.json()
        for row in data["data"]:
            assert row["platform"] == "YouTube"

    def test_engagement_progression(self):
        response = client.get("/api/v1/engagement/engagement-progression")
        assert response.status_code == 200
        data = response.json()
        snapshots = [r["snapshot_number"] for r in data["data"]]
        assert 1 in snapshots
        assert max(snapshots) <= 7

    def test_top_by_sentiment_default(self):
        response = client.get("/api/v1/engagement/top-by-sentiment")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 10

    def test_engagement_for_valid_campaign(self):
        response = client.get("/api/v1/engagement/by-campaign/CAM0000001")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] > 0

    def test_engagement_for_invalid_campaign_returns_404(self):
        response = client.get("/api/v1/engagement/by-campaign/INVALID")
        assert response.status_code == 404