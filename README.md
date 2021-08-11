# Kafka-Spark Project 

Meetup streaming api : http://stream.meetup.com/2/rsvps

## Architecture

Kafka : To persist the incoming streaming messages and deliver to spark application

Spark: Structured Streaming to process the data from kafka and write to a RDBMS


## Starting kafka-server:

After following "setup.sh" , 
To start zookeeper: 

```
zookeeper-server-start.sh ./kafka_2.13-2.8.0/config/zookeeper.properties
```
To start kafka-server 

```
 kafka-server-start.sh ./kafka_2.13-2.8.0/config/server.properties
```

Create a kafka topic using the command :
 - note : setup partitioins and replication factor according to the bootstrap servers you're using or configure them in ./config/server.properites

```
kafka-topics.sh --bootstrap-server localhost:9092 --create --topic my-topic --partitions 3 --replication-factor 2
```
## Deploying Spark Application:

'start' bash file: to deploy the spark driver program in the spark cluster

```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 --jars ~/spark-project/postgresJars/postgresql-42.2.23.jar spark.py

```

## Spark DataFrames

Spark consumes the data from the kafka-topic using kafka-consumer 

#### Reading from the kafka stream:

Spark application reads steaming data from spark for futher processing
```
            df = spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", bootstrap_server) \
                .option("subscribe", topic_name) \
                .option("startingOffsets","latest") \
                .load()
```


Then, spark converts the data into a df in the form:
- The 'value' field contains the json messages from the kafka-stream

```
 |-- key: binary (nullable = true)
 |-- value: binary (nullable = true)
 |-- topic: string (nullable = true)
 |-- partition: integer (nullable = true)
 |-- offset: long (nullable = true)
 |-- timestamp: timestamp (nullable = true)
 |-- timestampType: integer (nullable = true)
```


We extract the schema from the json data for Schema Inference and inserting the data to DataFrames using the code below: 

```
from pyspark.sql.types import StructType,StructField, StringType, IntegerType,DoubleType,ArrayType

schema = StructType([
        StructField("venue",StructType([ 
            StructField("venue_name",StringType(), True),
            StructField("lon",StringType(), True),
            StructField("lat",StringType(), True),
            StructField("venue_id",StringType(),True)
        ])),
        StructField("visibility",StringType(),True),
        StructField("response",StringType(),True),
        StructField("guests",StringType(),True),
        StructField("member",StructType([
            StructField("member_id",StringType(),True),
            StructField("photo",StringType(),True),
            StructField("member_name",StringType(),True)
        ])),
        StructField("rsvp_id",StringType(),True),
        StructField("mtime",StringType(),True),
        StructField("event",StructType([
            StructField("event_name",StringType(),True),
            StructField("event_id",StringType(),True),
            StructField("time",StringType(),True),
            StructField("event_url",StringType(),True)
        ])),
        StructField("group",StructType([
            StructField("group_topics",ArrayType(StructType([
                StructField("urlkey",StringType(),True),
                StructField("topic_name",StringType(),True)
            ]),True),True), #check this line again,
            
            StructField("group_city",StringType(),True),
            StructField("group_country",StringType(),True),
            StructField("group_id",StringType(),True),
            StructField("group_name",StringType(),True),
            StructField("group_lon",StringType(),True),
            StructField("group_urlname",StringType(),True),
            StructField("group_state",StringType(),True),
            StructField("group_lat",StringType(),True)
        ]))
    ])
```

Then, spark code deconstructs 'value' to the dataframe with columns below using the Schema Inference provided: 

```
root
 |-- venue: struct (nullable = true)
 |    |-- venue_name: string (nullable = true)
 |    |-- lon: string (nullable = true)
 |    |-- lat: string (nullable = true)
 |    |-- venue_id: string (nullable = true)
 |-- visibility: string (nullable = true)
 |-- response: string (nullable = true)
 |-- guests: string (nullable = true)
 |-- member: struct (nullable = true)
 |    |-- member_id: string (nullable = true)
 |    |-- photo: string (nullable = true)
 |    |-- member_name: string (nullable = true)
 |-- rsvp_id: string (nullable = true)
 |-- mtime: string (nullable = true)
 |-- event: struct (nullable = true)
 |    |-- event_name: string (nullable = true)
 |    |-- event_id: string (nullable = true)
 |    |-- time: string (nullable = true)
 |    |-- event_url: string (nullable = true)
 |-- group: struct (nullable = true)
 |    |-- group_topics: array (nullable = true)
 |    |    |-- element: struct (containsNull = true)
 |    |    |    |-- urlkey: string (nullable = true)
 |    |    |    |-- topic_name: string (nullable = true)
 |    |-- group_city: string (nullable = true)
 |    |-- group_country: string (nullable = true)
 |    |-- group_id: string (nullable = true)
 |    |-- group_name: string (nullable = true)
 |    |-- group_lon: string (nullable = true)
 |    |-- group_urlname: string (nullable = true)
 |    |-- group_state: string (nullable = true)
 |    |-- group_lat: string (nullable = true)
 |-- timestamp: timestamp (nullable = true)

```

Now, perform aggregating and groupby on the columns that should be stored in RDBMS/Hive datawarehouse using 
spark.sql.functions (groupBy,aggregate,alias,col,cast)

```
final_df = df.groupBy(func.col("event_name"), func.col("event_url"), func.col("time").alias("event_time") , func.col("group_name"),func.col("group_country"), func.col("group_state"),func.col("group_city"), (func.col("group_lat").cast(DoubleType())).alias("group_lat"), (func.col("group_lon").cast(DoubleType())).alias("group_lon"), (func.col("lat").cast(DoubleType())).alias("lat"),  (func.col("lon").cast(DoubleType())).alias("lon"), func.col("response")).agg(func.count(func.col("response")).alias("response_count"))

gives an output dataframe with the below Final chema: 


root
 |-- event_name: string (nullable = true)
 |-- event_url: string (nullable = true)
 |-- event_time: string (nullable = true)
 |-- group_name: string (nullable = true)
 |-- group_country: string (nullable = true)
 |-- group_state: string (nullable = true)
 |-- group_city: string (nullable = true)
 |-- group_lat: double (nullable = true)
 |-- group_lon: double (nullable = true)
 |-- lat: double (nullable = true)
 |-- lon: double (nullable = true)
 |-- response: string (nullable = true)
 |-- response_count: long (nullable = false)
```


## Spark Structured Streaming: 
Structured Streaming provides fast, scalable, fault-tolerant, end-to-end exactly-once stream processing without the user having to reason about streaming.

- Reference: 