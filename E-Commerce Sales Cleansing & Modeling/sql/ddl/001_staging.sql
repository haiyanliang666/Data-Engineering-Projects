CREATE TABLE IF NOT EXISTS raw_online_retail (
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity NUMERIC,
    invoice_date TIMESTAMP,
    unit_price NUMERIC(12, 4),
    customer_id TEXT,
    country TEXT,
    source_file TEXT,
    loaded_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cleansed_returns (
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity NUMERIC,
    invoice_date TIMESTAMP,
    unit_price NUMERIC(12, 4),
    customer_id TEXT,
    country TEXT,
    total_amount NUMERIC(14, 4),
    source_file TEXT,
    loaded_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rejected_online_retail (
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity NUMERIC,
    invoice_date TIMESTAMP,
    unit_price NUMERIC(12, 4),
    customer_id TEXT,
    country TEXT,
    total_amount NUMERIC(14, 4),
    source_file TEXT,
    loaded_at TIMESTAMP
);
