-- ============================================
-- SaaS Funnel Analysis — Revenue Analysis
-- Author: Aswath Roshan
-- Description: MRR breakdown by plan, channel,
-- churn analysis, subscriber growth
-- ============================================

-- Total MRR overview
SELECT
    SUM(mrr)   AS total_mrr,
    AVG(mrr)   AS avg_mrr_per_subscriber,
    COUNT(*)   AS total_subscribers
FROM subscriptions_clean
WHERE status = 'active';

-- MRR by plan
SELECT
    plan,
    COUNT(*)       AS subscribers,
    SUM(mrr)       AS total_mrr,
    ROUND(AVG(mrr), 2) AS avg_mrr
FROM subscriptions_clean
WHERE status = 'active'
GROUP BY plan
ORDER BY total_mrr DESC;

-- Churn analysis
SELECT
    churn_reason,
    COUNT(*) AS churned_users,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct_of_churned
FROM subscriptions_clean
WHERE status = 'churned'
GROUP BY churn_reason
ORDER BY churned_users DESC;

-- Monthly subscriber growth
SELECT
    strftime('%Y-%m', start_date) AS month,
    plan,
    COUNT(*) AS new_subscribers,
    SUM(mrr) AS new_mrr
FROM subscriptions_clean
GROUP BY month, plan
ORDER BY month, plan;