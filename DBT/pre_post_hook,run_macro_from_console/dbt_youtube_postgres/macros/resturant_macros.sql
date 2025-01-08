{% macro calculate_metrics(metrics) %}
    {% for metric in metrics %}
    SUM({{ metric }}) AS total_{{ metric }}{% if not loop.last %},{% endif %}
    {% endfor %}
{% endmacro %}

{% macro dynamic_price_adjustment(category, amount_column='amount') %}
    CASE
        {% if category == 'Appetizer' %}
        WHEN category = '{{ category }}' THEN {{ amount_column }} * 0.9
        {% elif category == 'Main Course' %}
        WHEN category = '{{ category }}' THEN {{ amount_column }} * 1.1
        {% elif category == 'Beverage' %}
        WHEN category = '{{ category }}' THEN {{ amount_column }} * 0.95
        {% else %}
        WHEN category = '{{ category }}' THEN {{ amount_column }} * 1.0
        {% endif %}
    END
{% endmacro %}

{% macro log_pre_hook(table_name) %}
    insert into hooks_log (hook_type, table_name, executed_at)
    values ('pre-hook', '{{table_name}}', current_timestamp);
{% endmacro %}

{% macro log_post_hook(table_name) %}
    insert into hooks_log (hook_type, table_name, executed_at)
    values ('post-hook', '{{table_name}}', current_timestamp);
{% endmacro %}

{% macro log_on_run_start() %}
    insert into run_log (run_phase, executed_at)
    values ('on-run-start', current_timestamp);
{% endmacro %}

{% macro log_on_run_end() %}
    insert into run_log (run_phase, executed_at)
    values ('on-run-end', current_timestamp);
{% endmacro %}


{% macro generate_customer_report(customer_id) %}
    {% set query %}
    select 
        customer_id,
        count(*) as transaction_count,
        sum(total_amount) as total_amount
    from {{ source('youtube', 'sales_transactions') }}
    where customer_id = {{ customer_id }}
    group by customer_id;
    {% endset %}
    
    {% set results = run_query(query) %}
    
    -- Log the results to the console
    {% for row in results %}
        {{ log(row, info=True) }}
    {% endfor %}
    
    {{ return(results) }}
{% endmacro %}

