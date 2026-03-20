-- ============================================
-- SaaS Funnel Analysis — Channel Analysis
-- Author: Aswath Roshan
-- Description: Conversion rates, user counts
-- and MRR contribution by acquisition channel
-- ============================================

-- Conversion rate by channel
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id)          AS total_users,
    COUNT(DISTINCT s.subscription_id)  AS converted_users,
    ROUND(
        COUNT(DISTINCT s.subscription_id) * 100.0 /
        COUNT(DISTINCT u.user_id), 1
    )                                  AS conversion_rate_pct
FROM users_clean u
LEFT JOIN subscriptions_clean s ON u.user_id = s.user_id
GROUP BY u.acquisition_channel
ORDER BY conversion_rate_pct DESC;

-- Average days to convert by channel
WITH trial_events AS (
    SELECT user_id, timestamp AS trial_start
    FROM events_clean
    WHERE event_name = 'trial_started'
),
conversion_events AS (
    SELECT user_id, timestamp AS converted_at
    FROM events_clean
    WHERE event_name = 'subscription_started'
),
time_to_convert AS (
    SELECT
        t.user_id,
        ROUND(julianday(c.converted_at) - julianday(t.trial_start), 0) AS days_to_convert
    FROM trial_events t
    JOIN conversion_events c ON t.user_id = c.user_id
)
SELECT
    u.acquisition_channel,
    COUNT(*)                           AS converted_users,
    ROUND(AVG(ttc.days_to_convert), 1) AS avg_days_to_convert,
    MIN(ttc.days_to_convert)           AS fastest,
    MAX(ttc.days_to_convert)           AS slowest
FROM time_to_convert ttc
JOIN users_clean u ON ttc.user_id = u.user_id
GROUP BY u.acquisition_channel
ORDER BY avg_days_to_convert;

-- Conversion rate by country
WITH user_counts AS (
    SELECT country, COUNT(*) AS total_users
    FROM users_clean
    GROUP BY country
),
converted_counts AS (
    SELECT u.country, COUNT(*) AS converted_users
    FROM users_clean u
    JOIN subscriptions_clean s ON u.user_id = s.user_id
    GROUP BY u.country
)
SELECT
    u.country,
    u.total_users,
    c.converted_users,
    ROUND(c.converted_users * 100.0 / u.total_users, 1) AS conversion_rate_pct
FROM user_counts u
JOIN converted_counts c ON u.country = c.country
ORDER BY conversion_rate_pct DESC;