import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.types import *

from pyspark.sql import DataFrame, Row
import datetime
from awsglue import DynamicFrame

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
glueContext.spark_session.builder.config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                                 .config("spark.sql.hive.convertMetastoreParquet", "false") \
                                 .getOrCreate()

job = Job(glueContext)
job.init(args['JOB_NAME'], args)


additional_options={
    "hoodie.table.name": "kinesis_person_data",
    "hoodie.datasource.write.storage.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.write.recordkey.field": "id",
    "hoodie.datasource.write.precombine.field": "timestamp",
    "hoodie.datasource.write.partitionpath.field": "country",
    "hoodie.datasource.write.hive_style_partitioning": "true",
    "hoodie.datasource.hive_sync.use_glue": "true",
    
    "hoodie.datasource.hive_sync.enable": "true",
    "hoodie.datasource.hive_sync.database": "kinesis_db",
    "hoodie.datasource.hive_sync.table": "kinesis_person_data",
    "hoodie.datasource.hive_sync.partition_fields": "country",
    'hoodie.datasource.hive_sync.sync_as_datasource': 'false',
    "hoodie.datasource.hive_sync.partition_extractor_class": "org.apache.hudi.hive.MultiPartKeysValueExtractor",
    "hoodie.datasource.hive_sync.use_jdbc": "false",
    "hoodie.datasource.hive_sync.mode": "hms",
    
    "hoodie.index.type": "GLOBAL_BLOOM",
    "hoodie.bloom.index.update.partition.path": "true"
}


output_path = "s3://kinesis_hudi/"
checkpoint_location = output_path + "cp/"
temp_path = output_path + "temp/"
now = datetime.datetime.now()
day = now.day

def process_data(data_frame,batchId):
    if (data_frame.count() > 0):
        dynamic_frame = DynamicFrame.fromDF(data_frame, glueContext, "from_data_frame")
        final_path = output_path + "kinesis_person_data" + "/ingest_day=" + "{:0>2}".format(str(day))
        df = dynamic_frame.toDF()
        df = df.withColumn('timestamp',df.timestamp.cast(TimestampType()))
        df.write.format("hudi") \
            .options(**additional_options) \
            .mode("append") \
            .save(final_path)

# Read from Kinesis Data Stream
kinesis_data = glueContext.create_data_frame.from_catalog( \
    database = "kinesis_db", \
    table_name = "kinesis_stream_table2", \
    additional_options = {"startingPosition": "TRIM_HORIZON", "inferSchema": "true"})

kinesis_data.printSchema()

glueContext.forEachBatch(frame = kinesis_data, batch_function = process_data, options = {"windowSize": "20 seconds", "checkpointLocation": checkpoint_location})



    
job.commit()