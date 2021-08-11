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
- [Deploying spark stuctured streaming applications using Jars] (https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html#deploying "Apache Spark Documentation" )

## Spark DataFrames

Spark consumes the data from the kafka-topic using built in kafka-consumer 

#### Reading from the kafka stream:

Spark application reads steaming data from Kafka for futher processing
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

Structured Streaming provides fast, scalable, fault-tolerant, end-to-end exactly-once stream processing without the users having to reason about streaming.

- Writing the data in batches to a RDBMS /Hive. For the projects purpose, I've used postgresql as persistent storage.
- Data in aggreagated in the dataframe and for each trigger interval specified, Spark Streaming writes out the data stream from DataFrames to specified Database/Datawarehouse/S3 url

```
# This code is used to write data in batches to the database/datawarehouse
# We specify the trigger time, which is the time interval between every .forEachBatch() invocation
        df\
        .writeStream\
        .trigger(processingTime="30 seconds")\
        .outputMode("update")\
        .foreachBatch(forEachBatchFunc)\
        .start()
```

The BatchFunction looks like this
```
batchDF_1.write.jdbc(url=jdbcURL, table="meetup_table" , mode="append",properties=postgresProps)
```

- Example of the final table written into database: 
```

+--------------------+--------------------+-------------+--------------------+-------------+-----------+-------------+---------+---------+---------+----------+--------+--------------+--------+
|          event_name|           event_url|   event_time|          group_name|group_country|group_state|   group_city|group_lat|group_lon|      lat|       lon|response|response_count|batch_id|
+--------------------+--------------------+-------------+--------------------+-------------+-----------+-------------+---------+---------+---------+----------+--------+--------------+--------+
|Nationals teams t...|https://www.meetu...|1629054000000|Austin Kayak Polo...|           us|         TX|       Austin|    30.24|   -97.76| 30.26759|-97.742989|     yes|             1|      80|
|Bi-monthly meetin...|https://www.meetu...|1628717400000|Cocktails and Con...|           us|         NC|    Charlotte|    35.14|   -80.94|35.116344| -80.95797|      no|             1|      80|
|Real Life Trading...|https://www.meetu...|1631055600000|Real Life Trading...|           us|         GA|      Atlanta|    33.86|    -84.4|-8.521147|  179.1962|     yes|             1|      80|
|INTERMEDIATE  PIC...|https://www.meetu...|1629235800000|South Jersey Pick...|           us|         NJ|  Cherry Hill|    39.88|   -74.97|  39.9693|-75.063416|     yes|             2|      80|
|­ Outdoor Pick-Up...|https://www.meetu...|1628949600000|Metro-Detroit Rec...|           us|         MI|      Livonia|    42.37|   -83.37|42.517296|-83.229309|     yes|             1|      80|
|Sketch Carl Schur...|https://www.meetu...|1629558000000|Central Park Sket...|           us|         NY|     New York|    40.72|   -73.98| 40.77495|-73.944786|      no|             1|      80|
|Carolina Fly Fish...|https://www.meetu...|1628721000000|    Women On The Fly|           us|         NC|     Davidson|    35.48|   -80.82|35.371643|-80.718675|     yes|             1|      80|
|Chopper Robot Tik...|https://www.meetu...|1628724600000|Nashville Fun Tim...|           us|         TN|    Nashville|    36.09|   -86.82|36.182686| -86.74881|      no|             1|      80|
|Badminton session...|https://www.meetu...|1629140400000|St.Laurence Badmi...|           gb|       null|       London|    51.44|    -0.02| 51.44211| -0.019953|     yes|             1|      80|
|Monday Badminton:...|https://www.meetu...|1629169200000|Vancouver Modest ...|           ca|         BC|    Vancouver|    49.24|   -123.1|49.195923|-123.12393|     yes|             1|      80|
|FREE EVENT! In-pe...|https://www.meetu...|1628722800000|Toronto Young and...|           ca|         ON|      Toronto|    43.74|   -79.36|43.656918|-79.402664|     yes|             2|      80|
|SATURDAY Badminto...|https://www.meetu...|1629000000000|Vancouver Modest ...|           ca|         BC|    Vancouver|    49.24|   -123.1|49.195923|-123.12393|     yes|             1|      80|
|Cider @ TreeRock ...|https://www.meetu...|1628719200000|30's and 40's Wom...|           us|         NC|    Asheville|    35.59|   -82.56|35.570423| -82.54523|      no|             1|      80|
|Webinar da biblio...|https://www.meetu...|1628805600000|    TOTVS Developers|           br|       null|    São Paulo|   -23.53|   -46.63|-8.521147|  179.1962|     yes|             3|      80|
|Women's Rooftop B...|https://www.meetu...|1630177200000|San Francisco Wom...|           us|         CA|San Francisco|    37.77|  -122.41|37.787178|-122.41299|     yes|             1|      80|
|Wednesday Magic i...|https://www.meetu...|1628717400000|          MTG Boston|           us|         MA|      Medford|    42.42|   -71.11|42.400806|-71.068794|     yes|             2|      80|
|UN VILLAGE AU SOL...|https://www.meetu...|1629223200000|The Manchester Fr...|           gb|       null|   Manchester|    53.48|    -2.23|-8.521147|  179.1962|     yes|             1|      80|
|IRL Thursday nigh...|https://www.meetu...|1628812800000|Road Runner Sport...|           us|         CO|   Broomfield|    39.88|  -105.11|39.836655| -105.0372|     yes|             1|      80|
|Drink and Dine - ...|https://www.meetu...|1629225000000|      The Cool Table|           gb|       null|   Manchester|    53.48|    -2.25|53.484776| -2.243357|     yes|             1|      80|
|#46982 London Win...|https://www.meetu...|1629223200000|London Singles Sp...|           gb|       null|       London|    51.52|     -0.1| 51.51794| -0.105571|     yes|             1|      80|
+--------------------+--------------------+-------------+--------------------+-------------+-----------+-------------+---------+---------+---------+----------+--------+--------------+--------+
only showing top 20 rows
```


- Reference: [ Spark Strucutred Streaming ] (https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)