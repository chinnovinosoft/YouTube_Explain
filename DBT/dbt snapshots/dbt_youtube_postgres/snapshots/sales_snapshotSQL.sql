{% snapshot sales_snapshotSQL %}

{{config(
        strategy='timestamp',
        unique_key='sale_id',
        updated_at='sale_timestamp',
        hard_deletes= 'new_record',
        )
}}

SELECT 
    *
FROM 
    {{ source('youtube', 'sales') }}

{% endsnapshot %}