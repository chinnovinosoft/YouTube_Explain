{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import sys\
from awsglue.transforms import *\
from awsglue.utils import getResolvedOptions\
from pyspark.context import SparkContext\
from awsglue.context import GlueContext\
from awsglue.job import Job\
from faker import Faker \
from datetime import datetime\
import pandas as pd \
\
## @params: [JOB_NAME]\
args = getResolvedOptions(sys.argv, ['JOB_NAME'])\
\
sc = SparkContext()\
glueContext = GlueContext(sc)\
spark = glueContext.spark_session\
glueContext.spark_session.builder.config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \\\
                                 .config("spark.sql.hive.convertMetastoreParquet", "false") \\\
                                 .getOrCreate()\
\
job = Job(glueContext)\
job.init(args['JOB_NAME'], args)\
job.commit()\
\
fake = Faker()\
data = []\
for i in range(5,10):\
    row = \{\
        "id": i + 1,\
        "name": fake.name(),\
        "city": fake.city(),\
        "address": fake.address(),\
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),\
        "country": fake.country(),\
        "state": fake.state(),\
    \}\
    data.append(row)\
pdf = pd.DataFrame(data)\
df = spark.createDataFrame(pdf)\
df.show(truncate=False)\
\
\
additional_options=\{\
    "hoodie.table.name": "faker_hudi",\
    "hoodie.datasource.write.storage.type": "COPY_ON_WRITE",\
    "hoodie.datasource.write.operation": "upsert",\
    "hoodie.datasource.write.recordkey.field": "id",\
    "hoodie.datasource.write.precombine.field": "timestamp",\
    "hoodie.datasource.write.partitionpath.field": "country",\
    "hoodie.datasource.write.hive_style_partitioning": "true",\
    "hoodie.datasource.hive_sync.use_glue": "true",\
    \
    "hoodie.datasource.hive_sync.enable": "true",\
    "hoodie.datasource.hive_sync.database": "hudi_db",\
    "hoodie.datasource.hive_sync.table": "faker_hudi",\
    "hoodie.datasource.hive_sync.partition_fields": "country",\
    'hoodie.datasource.hive_sync.sync_as_datasource': 'false',\
    "hoodie.datasource.hive_sync.partition_extractor_class": "org.apache.hudi.hive.MultiPartKeysValueExtractor",\
    "hoodie.datasource.hive_sync.use_jdbc": "false",\
    "hoodie.datasource.hive_sync.mode": "hms",\
    "path": "s3://",\
    \
    "hoodie.index.type": "GLOBAL_BLOOM",\
    "hoodie.bloom.index.update.partition.path": "true"\
\}\
\
df.write.format("hudi") \\\
    .options(**additional_options) \\\
    .mode("append") \\\
    .save()\
\
\
#--additional-python-modules faker==0.7.4\
#--conf spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false\
#--datalake-formats hudi }