#!/bin/bash


sudo apt-get update

apt install openjdk-8-jre-headless -y 
apt install scala

# instal spark from spark downloads 

wget https://apache.claz.org/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz 

tar xvf spark-1.3.1-bin-hadoop2.6.tgz

mv spark-1.3.1-bin-hadoop2.6 /usr/local/spark 

export PATH=$PATH:/usr/local/spark/bin

source ~/.bashrc


#  install kafka  [binaries 2.1.3 recommended] 

wget https://apache.claz.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz

tar xvf spark-1.3.1-bin-hadoop2.6.tgz

export PATH=~/kafka_2.13-2.8.0/bin:$PATH  # alternatively, add this to .bashrc



# setup data folders in kafka as data/zookeeper and data/kafka
# change config for zookeeper and sever to log into data folders
# Example below:  [in log-properites of kafka-server]

log.dirs=~/kafka_2.12-2.8.0/data/kafka 

# open kafka server to producer ip in server.properites

advertised.listeners=PLAINTEXT://[Your_procuder_ip] 

# and if necessary, change bootstrap_server properites



# setup postgres 

sudo apt install postgresql -y 

# next  change pg_hba.conf and restart : 
sudo service postgresql restart


# pip for pyspark

sudo apt install -y python3-pip

pip install kafka
pip install kafka-python