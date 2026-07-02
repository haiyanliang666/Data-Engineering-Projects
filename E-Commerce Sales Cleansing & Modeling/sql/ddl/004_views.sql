CREATE OR REPLACE VIEW vw_daily_revenue AS
SELECT
    d.full_date,
    SUM(f.total_amount) AS revenue,
    COUNT(DISTINCT f.invoice_no) AS invoice_count
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.full_date;

CREATE OR REPLACE VIEW vw_weekly_revenue AS
SELECT
    d.year,
    d.week,
    SUM(f.total_amount) AS revenue,
    COUNT(DISTINCT f.invoice_no) AS invoice_count
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.week;

CREATE OR REPLACE VIEW vw_top_products AS
SELECT
    p.stock_code,
    p.description,
    SUM(f.quantity) AS units_sold,
    SUM(f.total_amount) AS revenue
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.stock_code, p.description;

CREATE OR REPLACE VIEW vw_monthly_growth AS
WITH monthly AS (
    SELECT
        d.year,
        d.month,
        SUM(f.total_amount) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY d.year, d.month
)
SELECT
    year,
    month,
    revenue,
    revenue - LAG(revenue) OVER (ORDER BY year, month) AS revenue_change,
    CASE
        WHEN LAG(revenue) OVER (ORDER BY year, month) IS NULL THEN NULL
        WHEN LAG(revenue) OVER (ORDER BY year, month) = 0 THEN NULL
        ELSE ROUND(
            ((revenue - LAG(revenue) OVER (ORDER BY year, month))
            / LAG(revenue) OVER (ORDER BY year, month)) * 100,
            2
        )
    END AS growth_rate_percent
FROM monthly;
