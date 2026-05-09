"""
Pydantic schemas — define the shape of every API response.
This is what the API guarantees to return.
"""

from pydantic import BaseModel
from typing import Optional, List, Any


class APIResponse(BaseModel):
    """Standard wrapper for all API responses."""
    success: bool
    message: str
    data: Any
    total_records: Optional[int] = None


class PlatformRevenue(BaseModel):
    platform: str
    total_campaigns: int
    total_ad_spend: float
    total_revenue: float
    total_profit: float
    avg_roas: float
    avg_roi: float


class MonthlyRevenue(BaseModel):
    year: int
    month: int
    month_name: str
    quarter: str
    monthly_revenue: float
    monthly_profit: float
    monthly_ad_spend: float
    campaigns_run: int


class TopCampaign(BaseModel):
    campaign_id: str
    business_name: str
    business_category: str
    platform: str
    campaign_type: str
    season: str
    ad_spend: float
    revenue: float
    profit: float
    roi: float
    roas: float


class PlatformComparison(BaseModel):
    platform: str
    market_benchmark_ctr: float
    our_avg_ctr: float
    ctr_vs_benchmark_pct: float
    market_benchmark_cpc: float
    our_avg_cpc: float
    avg_roas: float
    total_campaigns: int


class AudienceAge(BaseModel):
    audience_age_group: str
    total_campaigns: int
    total_conversions: int
    avg_conversion_rate: float
    avg_ctr: float
    avg_roas: float


class ConversionFunnel(BaseModel):
    platform: str
    total_impressions: int
    total_clicks: int
    total_conversions: int
    impression_to_click_pct: float
    click_to_conversion_pct: float
    overall_funnel_pct: float