CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    invoice_no TEXT NOT NULL,
    product_key BIGINT NOT NULL REFERENCES dim_product(product_key),
    customer_key BIGINT NOT NULL REFERENCES dim_customer(customer_key),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    quantity NUMERIC NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 4) NOT NULL CHECK (unit_price > 0),
    total_amount NUMERIC(14, 4) NOT NULL CHECK (total_amount >= 0)
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_date_key ON fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product_key ON fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer_key ON fact_sales(customer_key);
