{{ config(
    materialized="table",
) }}

SELECT 
    DATE_TRUNC('month', order_date) AS order_month, 
    SUM(total_amount) AS total_amount_sum
FROM 
    {{ ref('customer_orders') }}
GROUP BY 
    order_month
ORDER BY 
    order_month
