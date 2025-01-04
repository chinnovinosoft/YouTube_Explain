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
