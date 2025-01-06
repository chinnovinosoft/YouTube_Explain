{{ config(
    materialized='incremental',
    incremental_strategy='microbatch',
    event_time='transaction_date',
    begin='2025-01-01',
    batch_size='day',
    unique_key='sales_id',
    concurrent_batches=false,
    lookback=3
) }}

WITH filtered_transactions AS (
    SELECT
        sales_id,
        transaction_date,
        customer_id,
        product_id,
        total_amount,
        current_timestamp as date_processed
    FROM {{ source('youtube', 'sales_transactions') }}
)

SELECT
    *
FROM filtered_transactions

