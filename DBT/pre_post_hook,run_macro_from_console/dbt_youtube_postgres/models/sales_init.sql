{{ config(
    materialized='table',
    pre_hook=log_pre_hook('{{this}}'),
    post_hook=log_post_hook('{{this}}')
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
