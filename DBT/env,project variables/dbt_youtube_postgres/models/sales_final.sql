{{ config(
    materialized='incremental',
) }}

SELECT
    sales_id,
    transaction_date,
    customer_id,
    product_id,
    total_amount,
    current_timestamp as date_processed
FROM {{ source('youtube', 'sales_transactions') }}
limit {{ var("limit", 1) }}

-- dbt run --vars '{"limit": 4}'