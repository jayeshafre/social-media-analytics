# Business Requirements — Social Media Analytics Platform

## Business Problem
Companies running ads across multiple social media platforms have no 
unified view of performance. They cannot easily answer:
- Which platform gives the best ROI?
- Which business category performs best on which platform?
- What audience segment converts the most?
- When is the best time to run campaigns?

## Our Platform Solves This

---

## Core Business Questions We Must Answer

### Revenue & Profitability
1. What is total revenue generated per platform?
2. Which platform has the highest ROAS?
3. Which business category generates the most profit?
4. What is monthly revenue trend across all platforms?
5. Which campaigns are in the top 10% for ROI?

### Campaign Performance
6. Which campaign type (Reel/Video/Carousel) performs best per platform?
7. What is average CTR per platform vs market benchmark?
8. Which campaign objective (Sales/Traffic/Leads) has best conversion rate?
9. How does campaign duration affect performance?
10. Which season (Diwali/Summer/Regular) drives the most conversions?

### Audience Insights
11. Which age group converts the most across platforms?
12. Does gender targeting affect ROI?
13. Which device type (Mobile/Desktop) has better conversion rates?
14. Which income level audience generates highest order values?

### Business Intelligence
15. Which businesses get the best ROI on LinkedIn vs Instagram?
16. Do influencer campaigns outperform non-influencer campaigns?
17. What is the CAC trend over time?
18. Which city generates the most conversions?

---

## Dashboard Requirements

| Dashboard         | Primary Audience | Key Metrics                    |
|-------------------|-----------------|--------------------------------|
| Executive Summary | CEO / CMO        | Revenue, ROI, ROAS, Top Platforms |
| Campaign Analytics| Marketing Team   | CTR, CPC, Conversion Rate      |
| Audience Insights | Product Team     | Demographics, Device, Location |
| Platform Comparison| Strategy Team   | Cross-platform benchmarking    |

---

## API Requirements

| Endpoint                    | Consumer         |
|-----------------------------|-----------------|
| GET /revenue/by-platform    | Dashboard        |
| GET /campaigns/top-roi      | Dashboard        |
| GET /audience/demographics  | Dashboard        |
| GET /platform/comparison    | Strategy Reports |
| GET /campaigns/{id}         | Campaign Detail  |