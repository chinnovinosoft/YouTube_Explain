{{ config(
    materialized='incremental',
) }}

select
    {{ dbt_utils.generate_surrogate_key(['customer_id', 'product_id']) }} as surrogate_key,
    {{ dbt_utils.star(source('youtube','sales_transactions'), except=['transaction_date']) }}
from {{ source('youtube','sales_transactions') }}
