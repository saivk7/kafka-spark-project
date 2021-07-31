from pyspark.sql import SparkSession
from pyspark.sql import functions as func
from pyspark.sql.types import StructType,StructField, StringType, IntegerType,ArrayType
#for kafkaf stream

def startSpark(topic_name,bootstrap_server):

    spark = SparkSession.builder \
            .master("local[*]") \
            .appName("Meetup Stream Processing app") \
            .getOrCreate()

    # setting log to error only
    spark.sparkContext.setLogLevel("Error")

    meetup_rsvp_df = spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", bootstrap_server) \
                .option("subscribe", topic_name) \
                .option("startingOffsets","latest") \
                .load()

    print("Priting the schema from the meetup_df \n ")
    meetup_rsvp_df.printSchema()


    meetup_rsvp_schema = StructType([
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
            StructField("group_stats",StringType(),True),
            StructField("group_lat",StringType(),True)
        ]))


    ])

    meetup_rsvp_df_1 = meetup_rsvp_df.selectExpr("CAST(value AS STRING)", "CAST(timestamp AS TIMESTAMP)")

    meetup_rsvp_df_2 = meetup_rsvp_df_1.select(func.from_json(func.col("value"),meetup_rsvp_schema).alias("message_deatils"),func.col("timestamp"))
    
    print("df2 schema is \n")
    meetup_rsvp_df_2.printSchema()

    meetup_rsvp_df_3  = meetup_rsvp_df_2.select(func.col("mesage_detail.*"),func.col("timestamp"))

    print("df3 schema is \n")
    meetup_rsvp_df_3.printSchema()


    meetup_rsvp_df_4 = meetup_rsvp_df_3.select(func.col("group.group_name"), func.col("group.group_country"),func.col("group.group_state"),func.col("group.group.city"),
    func.col("group.group_lat"),func.col("group.group_lon"), func.col("group.group_id"),func.col("group.group_topics"),func.col("member.member_name"),
    func.col("guests"),func.col("response"),func.col("venue.venue_name"),func.col("venue.lon"),func.col("venue.lat"), func.col("venue.venue_id"), func.col("visibility"),
    func.col("member.member_id"), func.col("event.event_name"), func.col("event.event_id"), func.col("event.time"), func.col("event.event_url")
    )

    print("df4 final schema")

    meetup_rsvp_df_4.printSchema()

    # writing stream to database


    

    spark.stop()
    

    """ meetup_rsvp_df_4.writeStream\
        .trigger(Trigger.ProcessingTime(30)) \
        .outputMode("update")
        .foreachBatch() """


    
    pass



def main():

    print('at main')
    topic_name = 'meetup-rsvp'
    bootstrap_server = '127.0.0.1:9092'

    #my sql and mogodb 

    
    username = 'doadmin'
    password = '152S7tVqBuG643y0'
    host = 'db-mongodb-nyc3-66302-forspark-ff47336e.mongo.ondigitalocean.com'
    port = 27017
    database = 'admin'
    protocol = 'mongodb+srv'

    mongoConnectionURL = "mongodb+srv://doadmin:152S7tVqBuG643y0@db-mongodb-nyc3-66302-forspark-ff47336e.mongo.ondigitalocean.com/admin?authSource=admin&tls=true&tlsCAFile=%3Creplace-with-path-to-CA-cert%3E"

    startSpark(topic_name,bootstrap_server,mongoConnectionURL)











    pass




if __name__ == "__main__":
    main()