-- Monthly revenue trends
SELECT month, ROUND(SUM(revenue_usd), 2) AS total_revenue_usd
FROM regional_revenue
GROUP BY month
ORDER BY month;

-- Weighted customer churn rate
SELECT ROUND(
    100.0 * SUM(churned_customers) / NULLIF(SUM(beginning_customers), 0),
    2
) AS churn_rate_pct
FROM customer_churn;

-- Q4 performance by region
SELECT
    region,
    SUM(revenue_usd) AS q4_revenue_usd,
    SUM(orders) AS q4_orders,
    ROUND(AVG(gross_margin_pct), 2) AS q4_average_margin_pct
FROM regional_revenue
WHERE quarter = 'Q4'
GROUP BY region
ORDER BY q4_revenue_usd DESC;

-- Employee satisfaction compared with industry standards
SELECT
    department,
    satisfaction_pct,
    industry_benchmark_pct,
    satisfaction_pct - industry_benchmark_pct AS benchmark_gap_pct,
    manager_effectiveness_pct,
    workload_balance_pct,
    learning_access_pct
FROM employee_satisfaction
WHERE quarter = 'Q4'
ORDER BY benchmark_gap_pct DESC;

-- Sales performance and customer-success policy indicators
SELECT
    region,
    SUM(sales_revenue_usd) AS annual_sales_revenue_usd,
    ROUND(
        100.0 * SUM(won_deals)
        / NULLIF(SUM(qualified_opportunities), 0),
        2
    ) AS win_rate_pct,
    ROUND(AVG(renewal_rate_pct), 2) AS renewal_rate_pct,
    ROUND(AVG(customer_satisfaction_pct), 2) AS customer_satisfaction_pct,
    ROUND(AVG(handoff_within_2_business_days_pct), 2) AS handoff_timeliness_pct,
    ROUND(AVG(success_plan_within_10_business_days_pct), 2) AS success_plan_timeliness_pct,
    ROUND(AVG(at_risk_action_plan_pct), 2) AS at_risk_action_plan_pct
FROM sales_customer_success
GROUP BY region
ORDER BY annual_sales_revenue_usd DESC;
