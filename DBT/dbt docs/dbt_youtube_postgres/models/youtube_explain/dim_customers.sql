{{ config(
    materialized="table",
) }}


with customers as (
    select * from {{ source('youtube','stg_customers') }}
),

accepted_email_domains as (
    select * from {{ source('youtube','top_level_email_domains') }}
),
	
check_valid_emails as (
    select
        customers.customer_id,
        customers.first_name,
        customers.last_name,
        customers.email,
	      coalesce (regexp_like(
            customers.email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        )
        = true
        and accepted_email_domains.tld is not null,
        false) as is_valid_email_address
    from customers
		left join accepted_email_domains
        on customers.email_top_level_domain = lower(accepted_email_domains.tld)
)

select * from check_valid_emails
