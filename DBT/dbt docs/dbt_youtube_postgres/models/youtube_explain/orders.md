{% docs customer_orders %}

This model captures every detail about customer orders by joining data from the `customers` and `orders` source tables in the `youtube` database.

Below are more details about orders:
- `/`  
  Overview of the orders, including customer and order details.
- `/about`  
  Provides information about the restaurants and menu details.
- `/team`  
  Represents the entire restaurant team involved in order processing.
- `/contact-us`  
  For more details, contact 000000.

This model is materialized as a table and includes pre-hooks and post-hooks for audit logging:
- **Pre-hook**: Logs the status as 'inprogress' in the `public.audit_log` table when the model starts running.
- **Post-hook**: Logs the status as 'completed' in the `public.audit_log` table when the model finishes running.

{% enddocs %}

{% docs __overview__ %}
# Customer Orders Playbook

This dbt project models and manages customer orders data by integrating information from multiple sources. It demonstrates best practices for building robust and scalable analytics workflows for e-commerce platforms.

This project includes:
- **Audit Logging**: Tracks the progress and completion of model execution with pre-hooks and post-hooks.
- **Lineage Tracking**: Ensures clear relationships between customers and orders.
- **Data Validation**: Implements comprehensive tests to ensure data quality, such as uniqueness, not-null constraints, and range validations.

For more details, refer to:
- **Documentation**: [Customer Orders Overview](#)
- **Source Code Repository**: [GitHub Repo](#)

{% enddocs %}

