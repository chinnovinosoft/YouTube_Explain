
WITH cte AS (
SELECT order_date,
       CASE 
           WHEN to_date(order_date::text, 'YYYY-MM-DD') IS NOT NULL THEN 'Valid Format'
           ELSE 'Invalid Format'
       END AS date_format_status
FROM {{ ref('customer_orders') }}
WHERE order_date IS NOT NULL
)
SELECT 
    *
FROM 
    cte
where date_format_status = 'Invalid Format'
