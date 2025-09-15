-- 1. Total sales by product
SELECT
    product_name,
    COUNT(*) as transaction_count,
    SUM(quantity) as total_units_sold,
    ROUND(SUM(total_price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(price_per_unit)::NUMERIC, 2) as avg_unit_price
FROM cleaned_sales
GROUP BY product_name
ORDER BY total_revenue DESC;

-- 2. Top customers by spending
SELECT
    customer_id,
    COUNT(*) as order_count,
    ROUND(SUM(total_price)::NUMERIC, 2) as total_spent
FROM cleaned_sales
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;

-- 3. Daily sales trend
SELECT
    transaction_date,
    COUNT(*) as daily_orders,
    ROUND(SUM(total_price)::NUMERIC, 2) as daily_revenue
FROM cleaned_sales
GROUP BY transaction_date
ORDER BY transaction_date;

-- 4. Data quality report
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT transaction_id) as unique_transactions,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product_name) as unique_products,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date
FROM cleaned_sales;

-- 5. Additional useful queries
-- Average order value by product
SELECT
    product_name,
    ROUND(AVG(total_price)::NUMERIC, 2) as avg_order_value,
    MIN(total_price) as min_order_value,
    MAX(total_price) as max_order_value
FROM cleaned_sales
GROUP BY product_name
ORDER BY avg_order_value DESC;

-- Monthly sales summary
SELECT
    EXTRACT(YEAR FROM transaction_date) as year,
    EXTRACT(MONTH FROM transaction_date) as month,
    COUNT(*) as order_count,
    ROUND(SUM(total_price)::NUMERIC, 2) as monthly_revenue
FROM cleaned_sales
GROUP BY year, month
ORDER BY year, month;

-- Product performance
SELECT
    product_name,
    COUNT(*) as orders,
    SUM(quantity) as total_quantity_sold,
    ROUND(SUM(total_price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(price_per_unit)::NUMERIC, 2) as avg_price
FROM cleaned_sales
GROUP BY product_name
ORDER BY total_revenue DESC;