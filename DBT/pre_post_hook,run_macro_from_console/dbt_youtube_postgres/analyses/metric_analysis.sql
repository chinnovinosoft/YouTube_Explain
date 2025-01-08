SELECT
    category,
    COUNT(*) AS total_items_sold,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_revenue_per_item
FROM {{ source('youtube','restaurants') }}
GROUP BY category
ORDER BY total_revenue DESC;
