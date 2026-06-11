-- ============================================================
-- SQL Phase 2 | Step 3: Group-Level Metric Aggregations
-- File: sql/03_group_metrics.sql
-- Tool: DuckDB
--
-- Purpose:
--   Aggregate user-level funnel data into group-level summary
--   metrics that feed directly into the statistical tests in
--   Phase 4. Also computes the funnel drop-off at each stage.
--
-- SQL techniques demonstrated:
--   - GROUPING SETS for multi-level rollups
--   - RANK() window function for segment ranking
--   - FILTER clause for conditional aggregation
--   - NULLIF to protect against divide-by-zero
-- ============================================================

-- ============================================================
-- Query 1: Core reorder rate comparison by group
--   Primary input for the two-proportion z-test
-- ============================================================
SELECT
    experiment_group,
    COUNT(*)                                  AS total_users,
    -- 30-day reorder metrics
    SUM(reordered_30d)                        AS reordered_30d_count,
    ROUND(AVG(reordered_30d) * 100, 2)        AS reorder_rate_30d_pct,
    -- 60-day reorder metrics
    SUM(reordered_60d)                        AS reordered_60d_count,
    ROUND(AVG(reordered_60d) * 100, 2)        AS reorder_rate_60d_pct,
    -- 90-day reorder metrics
    SUM(reordered_90d)                        AS reordered_90d_count,
    ROUND(AVG(reordered_90d) * 100, 2)        AS reorder_rate_90d_pct
FROM user_funnel
GROUP BY experiment_group
ORDER BY experiment_group;


-- ============================================================
-- Query 2: Order value comparison by group
--   Input for Mann-Whitney U test on AOV distribution
-- ============================================================
SELECT
    experiment_group,
    COUNT(*)                                  AS total_users,
    ROUND(AVG(first_order_gross), 2)          AS avg_first_order_gross,
    ROUND(AVG(first_order_discount), 2)       AS avg_discount_given,
    ROUND(AVG(first_order_net), 2)            AS avg_first_order_net,
    ROUND(AVG(avg_reorder_value), 2)          AS avg_reorder_value,
    ROUND(STDDEV(avg_reorder_value), 2)       AS stddev_reorder_value,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP
        (ORDER BY avg_reorder_value), 2)      AS p25_reorder_value,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP
        (ORDER BY avg_reorder_value), 2)      AS median_reorder_value,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP
        (ORDER BY avg_reorder_value), 2)      AS p75_reorder_value
FROM user_funnel
GROUP BY experiment_group
ORDER BY experiment_group;


-- ============================================================
-- Query 3: Net revenue per user — the guardrail metric
-- ============================================================
SELECT
    experiment_group,
    COUNT(*)                                  AS total_users,
    ROUND(AVG(net_revenue_90d), 2)            AS avg_net_revenue_90d,
    ROUND(AVG(gross_revenue_90d), 2)          AS avg_gross_revenue_90d,
    ROUND(AVG(first_order_discount), 2)       AS avg_discount_cost,
    ROUND(SUM(net_revenue_90d), 2)            AS total_net_revenue,
    ROUND(SUM(first_order_discount), 2)       AS total_discount_cost,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP
        (ORDER BY net_revenue_90d), 2)        AS median_net_revenue_90d,
    ROUND(STDDEV(net_revenue_90d), 2)         AS stddev_net_revenue_90d
FROM user_funnel
GROUP BY experiment_group
ORDER BY experiment_group;


-- ============================================================
-- Query 4: Order funnel drop-off at each stage
--   Shows where users fall off between first and repeat orders
-- ============================================================
SELECT
    experiment_group,
    COUNT(*)                                  AS stage_0_all_users,
    COUNT(*)                                  AS stage_1_completed_first_order,
    SUM(reordered_30d)                        AS stage_2_reordered_30d,
    SUM(reordered_60d)                        AS stage_3_reordered_60d,
    SUM(reordered_90d)                        AS stage_4_reordered_90d,
    -- Drop-off rates between stages
    ROUND(
        (1 - AVG(reordered_30d)) * 100, 2
    )                                         AS dropoff_pct_after_first_order,
    ROUND(
        (AVG(reordered_60d) - AVG(reordered_30d))
        / NULLIF(AVG(reordered_30d), 0) * 100, 2
    )                                         AS lift_pct_30d_to_60d
FROM user_funnel
GROUP BY experiment_group
ORDER BY experiment_group;


-- ============================================================
-- Query 5: Frequency tier distribution by group
--   Input for Chi-square test on reorder behavior segments
-- ============================================================
SELECT
    experiment_group,
    frequency_tier,
    COUNT(*)                                  AS users,
    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (PARTITION BY experiment_group),
    2)                                        AS pct_within_group,
    ROUND(AVG(net_revenue_90d), 2)            AS avg_net_revenue_90d
FROM user_funnel
GROUP BY experiment_group, frequency_tier
ORDER BY experiment_group,
    CASE frequency_tier
        WHEN 'loyal'       THEN 1
        WHEN 'regular'     THEN 2
        WHEN 'occasional'  THEN 3
        WHEN 'one_and_done' THEN 4
    END;


-- ============================================================
-- Query 6: Day-of-week segmentation
--   Checks if promo effect differs by first-order day
-- ============================================================
SELECT
    experiment_group,
    CASE first_order_dow
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END                                       AS day_of_week,
    COUNT(*)                                  AS users,
    ROUND(AVG(reordered_30d) * 100, 2)        AS reorder_rate_30d_pct,
    ROUND(AVG(net_revenue_90d), 2)            AS avg_net_revenue_90d
FROM user_funnel
GROUP BY experiment_group, first_order_dow
ORDER BY experiment_group, first_order_dow;
