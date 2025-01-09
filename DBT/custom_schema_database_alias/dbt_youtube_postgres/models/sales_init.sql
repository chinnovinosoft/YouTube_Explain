{{ config(
    materialized='table',
    schema='sales_schema',
    database="youtube",
    alias='sales_init2025'
) }}

with sales as (
    select * from {{ source('youtube','sales_transactions') }}
)
select 
    customer_id,
    count(*) as transaction_count,
    sum(total_amount) as total_amount
from sales
group by customer_id
