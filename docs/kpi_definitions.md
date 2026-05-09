# KPI Definitions — Social Media Advertising Analytics Platform

## Overview
This document defines every Key Performance Indicator (KPI) tracked 
in this platform. Every metric here maps directly to a column in our 
database or a calculated field in our SQL queries.

---

## 1. Click-Through Rate (CTR)
**Definition:** Percentage of people who saw the ad and clicked on it.  
**Formula:** `CTR = (Clicks / Impressions) × 100`  
**Unit:** Percentage (%)  
**Good Range:** 1–3% (varies by platform)  
**Business Meaning:** Measures how compelling the ad creative is.  
**Our Column:** `campaigns.ctr`

---

## 2. Cost Per Click (CPC)
**Definition:** How much the business paid for each click.  
**Formula:** `CPC = Ad Spend / Clicks`  
**Unit:** INR (₹)  
**Good Range:** Lower is better  
**Business Meaning:** Measures efficiency of ad spend per click.  
**Our Column:** `campaigns.cpc`

---

## 3. Cost Per Mille (CPM)
**Definition:** Cost per 1,000 impressions.  
**Formula:** `CPM = (Ad Spend / Impressions) × 1000`  
**Unit:** INR (₹)  
**Good Range:** Depends on platform and industry  
**Business Meaning:** Measures brand awareness campaign efficiency.  
**Calculated In:** SQL / API layer

---

## 4. Conversion Rate
**Definition:** Percentage of clicks that resulted in a purchase or lead.  
**Formula:** `Conversion Rate = (Conversions / Clicks) × 100`  
**Unit:** Percentage (%)  
**Good Range:** 2–5% is industry average  
**Business Meaning:** Measures how well the landing page converts visitors.  
**Our Column:** `campaigns.conversion_rate`

---

## 5. Return on Ad Spend (ROAS)
**Definition:** Revenue earned for every ₹1 spent on advertising.  
**Formula:** `ROAS = Revenue Generated / Ad Spend`  
**Unit:** Ratio (e.g. 4.5x means ₹4.5 earned per ₹1 spent)  
**Good Range:** Above 4x is considered healthy  
**Business Meaning:** Primary metric for ad campaign profitability.  
**Our Column:** `campaigns.roas`

---

## 6. Return on Investment (ROI)
**Definition:** Profit earned relative to the money invested in ads.  
**Formula:** `ROI = (Profit Generated / Ad Spend) × 100`  
**Unit:** Percentage (%)  
**Good Range:** Above 100% means doubling investment  
**Business Meaning:** True measure of campaign financial success.  
**Our Column:** `campaigns.roi`

---

## 7. Customer Acquisition Cost (CAC)
**Definition:** Total cost to acquire one new customer.  
**Formula:** `CAC = Total Ad Spend / Total New Customers Acquired`  
**Unit:** INR (₹)  
**Good Range:** Lower is better; must be less than Customer LTV  
**Business Meaning:** Tells us if acquiring customers is sustainable.  
**Calculated In:** SQL / API layer

---

## 8. Engagement Rate
**Definition:** Percentage of people who interacted with the ad.  
**Formula:** `Engagement Rate = (Likes + Comments + Shares + Saves) / Impressions × 100`  
**Unit:** Percentage (%)  
**Good Range:** 1–5% is healthy on most platforms  
**Business Meaning:** Measures content resonance with the audience.  
**Our Column:** `campaigns.engagement_rate`

---

## 9. Revenue Generated
**Definition:** Total revenue attributed to the campaign.  
**Unit:** INR (₹)  
**Business Meaning:** Direct business outcome of the campaign.  
**Our Column:** `campaigns.revenue_generated`

---

## 10. Profit Generated
**Definition:** Revenue minus cost of goods and ad spend.  
**Unit:** INR (₹)  
**Business Meaning:** Actual financial gain from the campaign.  
**Our Column:** `campaigns.profit_generated`

---

## 11. Bounce Rate (Derived)
**Definition:** Percentage of users who clicked but did NOT convert.  
**Formula:** `Bounce Rate = (1 - Conversion Rate) × 100`  
**Unit:** Percentage (%)  
**Business Meaning:** Signals landing page or offer mismatch.  
**Calculated In:** SQL / API layer

---

## Platform Benchmarks Reference

| Platform  | Avg CTR | Avg CPC (₹) | Best For          |
|-----------|---------|-------------|-------------------|
| Instagram | 0.8–1.5%| 15–40       | D2C, Fashion, Youth|
| Facebook  | 0.9–2%  | 10–35       | Broad Audiences   |
| YouTube   | 0.3–0.7%| 5–20        | Brand Awareness   |
| LinkedIn  | 0.3–0.6%| 60–150      | B2B, SaaS         |
| WhatsApp  | 2–5%    | 5–15        | Retargeting       |