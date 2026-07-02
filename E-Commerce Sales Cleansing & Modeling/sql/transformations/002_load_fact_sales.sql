TRUNCATE fact_sales RESTART IDENTITY;

INSERT INTO fact_sales (
    invoice_no,
    product_key,
    customer_key,
    date_key,
    quantity,
    unit_price,
    total_amount
)
SELECT
    r.invoice_no,
    p.product_key,
    c.customer_key,
    d.date_key,
    r.quantity,
    r.unit_price,
    r.quantity * r.unit_price AS total_amount
FROM raw_online_retail r
JOIN dim_product p ON p.stock_code = r.stock_code
JOIN dim_customer c ON c.customer_id = r.customer_id
JOIN dim_date d ON d.full_date = r.invoice_date::DATE
WHERE r.invoice_no IS NOT NULL
  AND r.stock_code IS NOT NULL
  AND r.customer_id IS NOT NULL
  AND r.invoice_date IS NOT NULL
  AND r.quantity > 0
  AND r.unit_price > 0;
