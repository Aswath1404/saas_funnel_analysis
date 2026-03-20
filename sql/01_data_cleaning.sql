-- ============================================
-- SaaS Funnel Analysis — Data Cleaning
-- Author:
-- Description: Creates clean views from raw 
-- CSV imports, fixes NULL strings, handles 
-- data type conversions
-- ============================================

-- Fix string NULLs in subscriptions table

UPDATE subscriptions
SET churned_date = NULL WHERE churned_date = 'NULL';

UPDATE subscriptions
SET churn_reason = NULL WHERE churn_reason = 'NULL';

UPDATE subscriptions
SET plan_upgraded_to = NULL WHERE plan_upgraded_to = 'NULL';

UPDATE subscriptions
SET upgrade_date = NULL WHERE upgrade_date = 'NULL';

UPDATE events
SET event_properties = NULL WHERE event_properties = 'NULL';

-- Create clean views with proper data types
CREATE VIEW users_clean AS
SELECT
    user_id,
    date(signup_date)       AS signup_date,
    date(trial_expires_on)  AS trial_expires_on,
    country,
    acquisition_channel,
    company_size,
    industry,
    user_segment
FROM users;

CREATE VIEW events_clean AS
SELECT
    event_id, user_id, session_id, event_name,
    datetime(timestamp)              AS timestamp,
    device_type,
    NULLIF(event_properties, 'NULL') AS event_properties
FROM events;

CREATE VIEW subscriptions_clean AS
SELECT
    subscription_id, user_id, plan, billing_cycle,
    CAST(mrr AS REAL)                  AS mrr,
    date(start_date)                   AS start_date,
    status,
    NULLIF(churned_date,     'NULL')   AS churned_date,
    NULLIF(churn_reason,     'NULL')   AS churn_reason,
    NULLIF(plan_upgraded_to, 'NULL')   AS plan_upgraded_to,
    NULLIF(upgrade_date,     'NULL')   AS upgrade_date
FROM subscriptions;