{{ config(
    materialized="table",
) }}

{% set pricing_adjustments = {
    "Appetizer": 0.9,   
    "Main Course": 1.1, 
    "Beverage": 0.95,  
    "Dessert": 1.0     
} 
%}
{% set last_date = '2025-01-31' %}

{# Hellooo Comment1 #}

SELECT
    item_name,
    category,
    amount AS original_amount,
    CASE 
    {% for category, multiplier in pricing_adjustments.items() %}
        WHEN category = '{{ category }}' THEN amount * {{ multiplier }}
    {% endfor %} 
    END AS adjusted_amount
FROM {{ source('youtube','restaurants') }}
where cast(sale_timestamp AS date) <= '{{ last_date }}'
