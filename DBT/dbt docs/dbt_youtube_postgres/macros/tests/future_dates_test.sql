{% test no_future_dates(model, column_name) %}

    select *
    from {{ model }}
    where {{ column_name }} > current_date

{% endtest %}
