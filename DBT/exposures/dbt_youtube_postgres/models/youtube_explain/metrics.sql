{{ config(
    materialized="table",
)
}}

{% set metrics = ["amount", "quantity"] %}

SELECT
    category,
    {{ calculate_metrics(metrics) }}
FROM {{ source('youtube','restaurants') }}
GROUP BY category
