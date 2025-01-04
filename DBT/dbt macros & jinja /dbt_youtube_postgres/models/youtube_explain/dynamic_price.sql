{{ config(
    materialized="table",
)
}}

SELECT
    item_name,
    category,
    amount,
    {{ dynamic_price_adjustment('Main Course') }} AS adjusted_price
FROM {{ source('youtube', 'restaurants') }}
