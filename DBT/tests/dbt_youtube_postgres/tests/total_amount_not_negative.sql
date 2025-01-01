
select total_amount 
from {{ref('customer_orders')}}
where total_amount <=0