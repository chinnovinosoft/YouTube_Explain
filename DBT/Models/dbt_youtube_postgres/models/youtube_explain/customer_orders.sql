{{ config(
    materialized="table",
    enabled=true,
    tags=["customer_orders"],
    pre_hook=["INSERT INTO public.audit_log (model_name, status) VALUES ('customer_orders' ,'inprogress' )"],
    post_hook=["INSERT INTO public.audit_log (model_name, status) VALUES ('customer_orders' ,'completed' )"],
    database="youtube",
    alias="customer_orders",
) }}


SELECT 
  a.customer_id, 
  a.name, 
  a.phone_number, 
  b.order_id, 
  b.order_date, 
  b.total_amount 
FROM 
  {{source('youtube','customers')}} a 
  INNER JOIN 
  {{source('youtube','orders')}} b 
ON 
  a.customer_id = b.customer_id

