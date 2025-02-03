from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="jinja_macro",
    start_date=datetime(2025, 2, 2),
    schedule="@daily",
    catchup=False,
) as dag:

    weekend_message = BashOperator(
        task_id="weekend_message",
        bash_command="""
            {% macro weekend_message(ds) -%}
                {% set day_name = execution_date.strftime('%A') %}
                {% if day_name in ["Saturday", "Sunday"] %}
                    echo "It's the weekend! Enjoy your day off."
                {% else %}
                    echo "It's a weekday. Time to hustle!"
                {% endif %}
            {%- endmacro %}

            {{ weekend_message(execution_date) }}
        """,
    )
    weekend_message
