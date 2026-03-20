-- ============================================
-- SaaS Funnel Analysis — Funnel Drop-off
-- Author: Aswath Roshan
-- Description: Analyses user progression 
-- through 7-stage funnel, calculates drop-off
-- rates at each stage
-- ============================================

-- Full funnel with drop-off percentages
WITH funnel AS (
    SELECT
        event_name,
        COUNT(DISTINCT user_id) AS users_at_stage
    FROM events_clean
    GROUP BY event_name
),
funnel_ordered AS (
    SELECT
        event_name,
        users_at_stage,
        CASE event_name
            WHEN 'trial_started'          THEN 1
            WHEN 'onboarding_completed'   THEN 2
            WHEN 'project_created'        THEN 3
            WHEN 'task_added'             THEN 4
            WHEN 'teammate_invited'       THEN 5
            WHEN 'integration_connected'  THEN 6
            WHEN 'subscription_started'   THEN 7
        END AS stage_order
    FROM funnel
)
SELECT
    stage_order,
    event_name,
    users_at_stage,
    ROUND(users_at_stage * 100.0 / MAX(users_at_stage) OVER(), 1) AS pct_of_total,
    LAG(users_at_stage) OVER(ORDER BY stage_order) - users_at_stage AS users_dropped,
    ROUND(
        (LAG(users_at_stage) OVER(ORDER BY stage_order) - users_at_stage) * 100.0 /
        LAG(users_at_stage) OVER(ORDER BY stage_order), 1
    ) AS drop_off_pct
FROM funnel_ordered
ORDER BY stage_order;

-- Funnel by acquisition channel
WITH channel_funnel AS (
    SELECT
        u.acquisition_channel,
        e.event_name,
        COUNT(DISTINCT e.user_id) AS users
    FROM events_clean e
    JOIN users_clean u ON e.user_id = u.user_id
    GROUP BY u.acquisition_channel, e.event_name
)
SELECT *
FROM channel_funnel
ORDER BY acquisition_channel, event_name;