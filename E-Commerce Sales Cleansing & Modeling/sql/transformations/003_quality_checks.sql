DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM fact_sales WHERE invoice_no IS NULL) THEN
        RAISE EXCEPTION 'fact_sales invoice_no contains nulls';
    END IF;

    IF EXISTS (SELECT 1 FROM fact_sales WHERE quantity < 0) THEN
        RAISE EXCEPTION 'fact_sales quantity contains negative values';
    END IF;

    IF EXISTS (SELECT 1 FROM fact_sales WHERE total_amount < 0) THEN
        RAISE EXCEPTION 'fact_sales total_amount contains negative values';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM fact_sales f
        LEFT JOIN dim_product p ON p.product_key = f.product_key
        LEFT JOIN dim_customer c ON c.customer_key = f.customer_key
        LEFT JOIN dim_date d ON d.date_key = f.date_key
        WHERE p.product_key IS NULL OR c.customer_key IS NULL OR d.date_key IS NULL
    ) THEN
        RAISE EXCEPTION 'fact_sales contains invalid dimension keys';
    END IF;

    IF (SELECT COALESCE(SUM(total_amount), 0) FROM fact_sales) = 0 THEN
        RAISE EXCEPTION 'fact_sales total revenue is zero';
    END IF;
END $$;
