-- ============================================================
-- SQL Phase 2 | Step 1: Load data and simulate experiment
-- File: sql/01_experiment_assignment.sql
-- Tool: DuckDB
-- Dataset: orders.csv (230,713 orders | 50,000 users)
--
-- Purpose:
--   Load the orders dataset into DuckDB and randomly assign
--   each user to control (A) or treatment (B) group.
--   Treatment group receives a simulated 20% first-order discount.
-- ============================================================

CREATE OR REPLACE TABLE raw_orders AS
SELECT
    order_id,
    user_id,
    order_number,
    order_dow,
    order_hour_of_day,
    days_since_prior_order,
    days_since_first_order,
    order_value
FROM read_csv_auto('data/orders.csv');

SELECT
    COUNT(*)                          AS total_orders,
    COUNT(DISTINCT user_id)           AS unique_users,
    MIN(order_number)                 AS min_order_num,
    MAX(order_number)                 AS max_order_num,
    ROUND(AVG(order_value), 2)        AS avg_order_value,
    ROUND(MAX(days_since_first_order))AS max_days_tracked
FROM raw_orders;

-- ============================================================
-- Step 2: Assign users to control or treatment
-- Hash-based deterministic 50/50 split — fully reproducible
-- ============================================================

CREATE OR REPLACE TABLE user_experiment_groups AS
SELECT
    user_id,
    CASE
        WHEN ABS(hash(CAST(user_id AS VARCHAR))) % 2 = 0
        THEN 'control'
        ELSE 'treatment'
    END AS experiment_group,
    MAX(CASE WHEN order_number = 1 THEN order_value END)
        AS first_order_value
FROM raw_orders
GROUP BY user_id;

SELECT
    experiment_group,
    COUNT(*)                              AS users,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER(), 2)          AS pct_of_total,
    ROUND(AVG(first_order_value), 2)      AS avg_first_order_value
FROM user_experiment_groups
GROUP BY experiment_group
ORDER BY experiment_group;

-- ============================================================
-- Step 3: Build enriched orders table with discount applied
-- ============================================================

CREATE OR REPLACE TABLE orders_enriched AS
SELECT
    o.order_id,
    o.user_id,
    o.order_number,
    o.order_dow,
    o.order_hour_of_day,
    o.days_since_prior_order,
    o.days_since_first_order,
    o.order_value                         AS gross_order_value,
    g.experiment_group,
    CASE
        WHEN g.experiment_group = 'treatment'
         AND o.order_number = 1
        THEN ROUND(o.order_value * 0.20, 2)
        ELSE 0.00
    END                                   AS discount_amount,
    CASE
        WHEN g.experiment_group = 'treatment'
         AND o.order_number = 1
        THEN ROUND(o.order_value * 0.80, 2)
        ELSE o.order_value
    END                                   AS net_order_value
FROM raw_orders o
JOIN user_experiment_groups g
    ON o.user_id = g.user_id;

SELECT
    experiment_group,
    COUNT(*)                              AS total_orders,
    COUNT(DISTINCT user_id)               AS unique_users,
    ROUND(AVG(gross_order_value), 2)      AS avg_gross_value,
    ROUND(AVG(discount_amount), 2)        AS avg_discount,
    ROUND(AVG(net_order_value), 2)        AS avg_net_value
FROM orders_enriched
GROUP BY experiment_group
ORDER BY experiment_group;
