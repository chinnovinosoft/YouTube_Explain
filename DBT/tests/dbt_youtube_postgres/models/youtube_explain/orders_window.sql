{{ config(
    materialized="table",
) }}

With orders as (
    select * from {{source('youtube','orders')}} 
),
customer_order_totals as (
    select
        orders.customer_id AS customer_id,
        orders.order_id AS order_id,
        orders.total_amount as total_amount,
        cast(sum(total_amount) over (partition by customer_id order by order_date) as decimal(10, 3)) as running_total
    from orders
)
select * from customer_order_totals
