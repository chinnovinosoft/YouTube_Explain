{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import sys\
import datetime\
import boto3\
import base64\
from pyspark.sql import DataFrame, Row\
from pyspark.context import SparkContext\
from pyspark.sql.types import *\
from pyspark.sql.functions import *\
from awsglue.transforms import *\
from awsglue.utils import getResolvedOptions\
from awsglue.context import GlueContext\
from awsglue.job import Job\
from awsglue import DynamicFrame\
\
args = getResolvedOptions(sys.argv, \\\
                            ['JOB_NAME'])\
\
sc = SparkContext()\
glueContext = GlueContext(sc)\
spark = glueContext.spark_session\
job = Job(glueContext)\
job.init(args['JOB_NAME'], args)\
\
\
output_path = "s3:///"\
checkpoint_location = output_path + "cp/"\
temp_path = output_path + "temp/"\
now = datetime.datetime.now()\
day = now.day\
\
def process_data(data_frame,batchId):\
    if (data_frame.count() > 0):\
        dynamic_frame = DynamicFrame.fromDF(data_frame, glueContext, "from_data_frame")\
        final_path = output_path + "person_data" + "/ingest_day=" + "\{:0>2\}".format(str(day))\
        s3sink = glueContext.write_dynamic_frame.from_options(frame = dynamic_frame, connection_type = "s3", connection_options = \{"path": final_path\}, format = "json", transformation_ctx = "s3sink")\
\
# Read from Kinesis Data Stream\
kinesis_data = glueContext.create_data_frame.from_catalog( \\\
    database = "kinesis_db", \\\
    table_name = "kinesis_stream_table", \\\
    additional_options = \{"startingPosition": "TRIM_HORIZON", "inferSchema": "true"\})\
\
kinesis_data.printSchema()\
\
glueContext.forEachBatch(frame = kinesis_data, batch_function = process_data, options = \{"windowSize": "20 seconds", "checkpointLocation": checkpoint_location\})\
job.commit()}