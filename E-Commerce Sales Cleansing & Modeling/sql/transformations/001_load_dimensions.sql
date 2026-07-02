INSERT INTO dim_product (stock_code, description)
SELECT DISTINCT stock_code, MAX(description) AS description
FROM raw_online_retail
WHERE stock_code IS NOT NULL
GROUP BY stock_code
ON CONFLICT (stock_code) DO UPDATE
SET description = EXCLUDED.description;

INSERT INTO dim_customer (customer_id, country)
SELECT DISTINCT customer_id, MAX(country) AS country
FROM raw_online_retail
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ON CONFLICT (customer_id) DO UPDATE
SET country = EXCLUDED.country;

INSERT INTO dim_date (date_key, full_date, year, quarter, month, week, day_of_week)
SELECT DISTINCT
    TO_CHAR(invoice_date::DATE, 'YYYYMMDD')::INTEGER AS date_key,
    invoice_date::DATE AS full_date,
    EXTRACT(YEAR FROM invoice_date)::INTEGER AS year,
    EXTRACT(QUARTER FROM invoice_date)::INTEGER AS quarter,
    EXTRACT(MONTH FROM invoice_date)::INTEGER AS month,
    EXTRACT(WEEK FROM invoice_date)::INTEGER AS week,
    EXTRACT(ISODOW FROM invoice_date)::INTEGER AS day_of_week
FROM raw_online_retail
WHERE invoice_date IS NOT NULL
ON CONFLICT (date_key) DO NOTHING;
