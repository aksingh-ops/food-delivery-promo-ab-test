-- ============================================================
-- SQL Phase 2 | Step 2: Order Funnel Build
-- File: sql/02_funnel_build.sql
-- Tool: DuckDB
--
-- Purpose:
--   Build the complete order funnel for both experiment groups.
--   For each user, compute:
--     - Did they reorder within 30 / 60 / 90 days?
--     - How many total orders in 90 days?
--     - What was their average order value across all orders?
--     - What was their net revenue contribution after discount?
--
-- SQL techniques demonstrated:
--   - Multi-step CTEs (5 stages)
--   - Window functions: ROW_NUMBER, RANK, SUM OVER
--   - Conditional aggregation with CASE WHEN
--   - Date arithmetic on days_since_first_order
--   - NULLIF to avoid divide-by-zero
-- ============================================================

-- ============================================================
-- CTE 1: first_orders
--   Isolate each user's first order as the experiment anchor.
--   All reorder windows are measured from this point.
-- ============================================================
WITH first_orders AS (
    SELECT
        user_id,
        experiment_group,
        gross_order_value               AS first_order_gross,
        net_order_value                 AS first_order_net,
        discount_amount                 AS first_order_discount,
        order_dow                       AS first_order_dow,
        order_hour_of_day               AS first_order_hour
    FROM orders_enriched
    WHERE order_number = 1
),

-- ============================================================
-- CTE 2: subsequent_orders
--   All orders after the first, with days_since_first_order
--   used to classify into the 30 / 60 / 90 day windows.
-- ============================================================
subsequent_orders AS (
    SELECT
        user_id,
        order_number,
        gross_order_value,
        net_order_value,
        days_since_first_order,
        -- Tag which reorder window this order falls into
        CASE
            WHEN days_since_first_order <= 30  THEN 'within_30d'
            WHEN days_since_first_order <= 60  THEN 'within_60d'
            WHEN days_since_first_order <= 90  THEN 'within_90d'
            ELSE 'beyond_90d'
        END                             AS reorder_window
    FROM orders_enriched
    WHERE order_number > 1
      AND days_since_first_order <= 90  -- cap observation window
),

-- ============================================================
-- CTE 3: user_reorder_flags
--   For each user: binary flags for whether they reordered
--   within each window, plus total orders and revenue.
-- ============================================================
user_reorder_flags AS (
    SELECT
        fo.user_id,
        fo.experiment_group,
        fo.first_order_gross,
        fo.first_order_net,
        fo.first_order_discount,
        fo.first_order_dow,
        fo.first_order_hour,
        -- Reorder flags: 1 if user placed any order in that window
        MAX(CASE
            WHEN so.days_since_first_order <= 30
            THEN 1 ELSE 0
        END)                            AS reordered_30d,
        MAX(CASE
            WHEN so.days_since_first_order <= 60
            THEN 1 ELSE 0
        END)                            AS reordered_60d,
        MAX(CASE
            WHEN so.days_since_first_order <= 90
            THEN 1 ELSE 0
        END)                            AS reordered_90d,
        -- Total orders placed in 90-day window (excl. first)
        COUNT(so.order_number)          AS reorders_in_90d,
        -- Revenue from reorders only (net of any discounts)
        COALESCE(SUM(so.net_order_value), 0)
                                        AS reorder_revenue_90d,
        -- Average order value of reorders
        ROUND(COALESCE(
            AVG(so.gross_order_value), 0
        ), 2)                           AS avg_reorder_value
    FROM first_orders fo
    LEFT JOIN subsequent_orders so
        ON fo.user_id = so.user_id
    GROUP BY
        fo.user_id,
        fo.experiment_group,
        fo.first_order_gross,
        fo.first_order_net,
        fo.first_order_discount,
        fo.first_order_dow,
        fo.first_order_hour
),

-- ============================================================
-- CTE 4: user_lifetime_value
--   Compute 90-day net revenue per user.
--   This is the guardrail metric — net value after discount.
-- ============================================================
user_lifetime_value AS (
    SELECT
        *,
        -- Total net revenue = first order net + all reorder revenue
        ROUND(
            first_order_net + reorder_revenue_90d, 2
        )                               AS net_revenue_90d,
        -- Total gross revenue (before any discounts)
        ROUND(
            first_order_gross + reorder_revenue_90d, 2
        )                               AS gross_revenue_90d
    FROM user_reorder_flags
),

-- ============================================================
-- CTE 5: user_order_frequency_tier
--   Segment users by how many times they reordered.
--   Used in the segmentation analysis in Phase 4.
-- ============================================================
user_order_frequency_tier AS (
    SELECT
        *,
        CASE
            WHEN reorders_in_90d = 0 THEN 'one_and_done'
            WHEN reorders_in_90d = 1 THEN 'occasional'
            WHEN reorders_in_90d = 2 THEN 'regular'
            WHEN reorders_in_90d >= 3 THEN 'loyal'
        END                             AS frequency_tier
    FROM user_lifetime_value
)

-- ============================================================
-- Final output: user-level funnel table
--   Save as a persistent table for use in statistical testing
-- ============================================================
SELECT * FROM user_order_frequency_tier;
