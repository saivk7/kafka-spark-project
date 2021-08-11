import requests
from kafka import KafkaProducer  #imports the producer client 
import json
import time


def startProducer(topic_name, bootstrap_server , dataURL):
    print("Starting Kafka Producer")
    #serializer function 

    serialize = lambda m: json.dumps(m).encode('utf-8')
    kafka_producer = KafkaProducer(bootstrap_servers=bootstrap_server, value_serializer= serialize)

    while True:
        try:
            stream_api_response = requests.get(dataURL, stream=True)
            if stream_api_response.status_code==200:
                
                print("Connected to the data streaming URL")

                for message in stream_api_response.iter_lines():
                    
                    print("Message Recieved \n \n " )
                    print(message)

                    json_message = json.loads(message)
                    print('\n \n after loads \n \n ')
                    print("sending to kafka type: " ,type(json_message), "message: " ,json_message)

                    kafka_producer.send(topic_name,json_message)
                    print("message sent!")
                    time.sleep(1)

            else:
                print('Error Status code ' , stream_api_response.status_code)
                raise Exception('Error from streaming data API')
                
        except Exception as e:

            print("Error in streaming URL  ", e )


def main():
    
    # URL of the straming data
    URL = 'https://stream.meetup.com/2/rsvps'
    
    # topic name to push the data 
    topic_name = "meetup-rsvp"
    
    # kafka server address
    bootstrap_server = 'localhost:9092'

    startProducer(topic_name,bootstrap_server,URL)




if __name__ == "__main__":
    main()