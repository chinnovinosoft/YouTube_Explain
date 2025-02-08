import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from awsglue.job import Job

# Parse job arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from the Glue catalog table (populated by the crawler)
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="glue_db_airflow",      
    table_name="glue_table_airflow",      
    transformation_ctx="datasource"
)

# Optional: Apply transformations (e.g., filtering, mapping, etc.)
transformed = datasource  # In this sample, we leave the data unchanged

# Write the data to a destination S3 path in Parquet format
glueContext.write_dynamic_frame.from_options(
    frame=transformed,
    connection_type="s3",
    connection_options={"path": "s3://praveen-airflow-glue/glue_target_data/"},
    format="parquet",
    transformation_ctx="datasink"
)

job.commit()
