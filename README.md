# SaaS Funnel Analysis

**Tools:** SQL (SQLite) · Power BI · Python · DAX  
**Dataset:** Synthetic — 50,000 users · 205,727 events · 9,347 subscribers  
**Type:** End-to-end product analytics project

---

## Business Context

A B2B SaaS productivity tool (India-first, expanding globally) 
wants to understand why only 18.7% of trial users convert to 
paid subscribers — and what drives the drop-off at each stage.

---

## Dataset

Custom synthetic dataset built from scratch using Python — 
designed to simulate realistic B2B SaaS behavior including:
- Acquisition channel bias (referral converts better than paid ads)
- Country-level conversion differences (India 15% vs USA 24%)
- Realistic time gaps between funnel events
- Business-hours timestamp distribution

3 relational tables:
| Table | Rows | Description |
|-------|------|-------------|
| users | 50,000 | User profiles, channels, segments |
| events | 205,727 | Full funnel event log |
| subscriptions | 9,347 | Revenue, plans, churn data |

---

## Funnel Results

| Stage | Users | Drop-off |
|-------|-------|----------|
| Trial Started | 50,000 | — |
| Onboarding Completed | 39,786 | -20.4% |
| Project Created | 34,515 | -13.2% |
| Task Added | 29,626 | -14.2% |
| Teammate Invited | 23,231 | -21.6% |
| Integration Connected | 19,222 | -17.3% |
| Subscription Started | 9,347 | -51.4% |

---

## Key Insights

1. **20.4% drop at onboarding** — 1 in 5 users never completes 
   setup. Simplifying onboarding is the fastest growth lever.

2. **Referral converts best (20.8%)** — highest conversion rate 
   of all channels. A formal referral program would scale this.

3. **India converts at 15% vs USA at 24%** — price sensitivity 
   is a barrier. INR billing or a lower-priced India plan recommended.

4. **51.4% final drop** — half of deeply engaged users don't 
   subscribe. Trigger a conversion email at integration_connected stage.

5. **Average 24 days to convert** — longer than the 14-day trial. 
   Extend trial to 21 days or send strong conversion email at day 14.

---

## Dashboard

3-page Power BI dashboard covering Acquisition, Funnel, and Revenue.

![Acquisition Overview](https://raw.githubusercontent.com/Aswath1404/saas_funnel_analysis/main/dashboard/pg1_Acquisition.png)
![Funnel Analysis](https://raw.githubusercontent.com/Aswath1404/saas_funnel_analysis/main/dashboard/pg2_Funnel.png)
![Revenue & Conversion](https://raw.githubusercontent.com/Aswath1404/saas_funnel_analysis/main/dashboard/pg3_Revenue.png)

---

## Repository Structure
```
├── data/               # Clean CSV datasets
├── sql/                # SQL queries (cleaning, funnel, channel, revenue)
├── python/             # Dataset generation script
├── dashboard/          # Power BI dashboard screenshots
└── writeup/            # Project summary document
```

---

## Skills Demonstrated

- Relational database design (3 normalized tables)
- Data cleaning and NULL handling in SQL
- Funnel analysis using CTEs and window functions
- DAX measures in Power BI
- Product thinking — insights tied to business recommendations