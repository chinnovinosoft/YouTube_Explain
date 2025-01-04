
select total_amount_sum 
from {{ref('orders_by_month')}}
where total_amount_sum < 100