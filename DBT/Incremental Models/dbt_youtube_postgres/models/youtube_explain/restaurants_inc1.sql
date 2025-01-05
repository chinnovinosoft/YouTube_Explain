-- models/incremental_merge_model.sql

{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='surrogate_key'
) }}

SELECT
    surrogate_key,
    category,
    item_name,
    amount,
    quantity,
    payment_method,
    sale_timestamp,
    sale_date
FROM {{ source('youtube', 'source_indian_restaurant_data') }}

{% if is_incremental() %}
    WHERE sale_timestamp > (SELECT COALESCE(MAX(sale_timestamp), '1900-01-01') FROM {{ this }})
{% endif %}
