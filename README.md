## Setup
Before running docker compose you need to run following commands:
```
sudo sysctl -w vm.max_map_count=262144
useradd hadoop
groupadd hadoop
sudo usermod -aG hadoop hadoop
```

Also, you need to have docker and docker compose plugin <= 2.29.2 installed.
newer versions do not allow hyphen in variable name

To start run entire setup execute:
``` bash
    ./setup/initialize_host.sh && ./setup/run.sh
```

## Nifi tips & tricks
* to use PutHdfs and the like set hadoop configuration properties to "/opt/config/hdfs-site.xml,/opt/config/core-site.xml"
* DO NOT CHANGE the name of the namenode container as nifi relies on this name to resolve it


## Where all guys are?
Mapping of addresses of specific components:
* Hadoop UI - https://localhost:9870
* webHDFS - https://localhost:9870
* pyspark executable - `/opt/spark/spark-3.5.0-bin-hadoop3/bin/pyspark` on namenode
* kafka - localhost:9092
* redis - localhost:6739
* elastic - localhost:9200
* kibana - localhost:5601
* nifi - http://localhost:8443/nifi (user - user, password - useruseruser)

## Storage
**HDFS**:
* `/crypto/blockchain/transactions` - transaction data stored in parquet files partitioned by date
* `/crypto/exchange/ticker` - ticker data stored in parquet files partitioned by date
* `/crypto/news/data` - incremental snapshot of news where version is a timestamp of snapshot load
* `/user/hadoop/model.model` - path where model is stored

**Elastic Indexes**:
CREATE INDICES BEFORE RUNNING SPARK PROCESSESS
CREATE Mapping of timestamp field to date type!!
* `predictions` - an index with online features + 0-1 prediction
* `transactions` - an index with transactions copied from HDFS
* `tickers` - an index with tickers copied from HDFS
* `roi` - an index with calculated model's ROI per ticker

**Kibana Dashboard**:
to load the dashboard:
1. Stack Management -> Kibana: Saved objects -> Import -> upload the `dashboard.ndjson` file

**Hive tables**:
* `training_data.full_training_dataset` - table with full training data created using offline logic

**Redis**:
* sentiment aggregates stored under keys: `(coindesk|cointelegraph|cryptocurrency_news)_(avg|stg|min|max)_sentiment`

## Spark processes
To run any of the described process you need to go to namenode - `docker exec -it namenode /bin/bash`.
### News to redis
Batch process extracting sentiment aggregates from newest version of news from HDFS and writing it to Redis under keys described above.
```bash
PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process news_to_redis
```
### Logs to elastic
Batch process that copies tickers and transactions logs from HDFS to Elastic to indexes `tickers`, `transactions`.
```bash
PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process logs_to_elastic
```
### Training data
Batch process which reads data from all the sources on HDFS and generates `training_data.full_training_dataset` on Hive.
```bash
PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process training_data
```
### Model training
Batch process that reads data from `training_data.full_training_dataset`, performs train-test split (last day is a test, the rest is train) and trains logistic regression and saves it to `/user/hadoop/model.model`.
```bash
PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process model_training
```
### Online ML
Stream process that online ingests data from Redis, calculates real-time aggregates, extracts feature vector, makes predictions using model from `/user/hadoop/model.model` and writes it to `predictions` index in Elastic in online manner.
```bash
PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process online_ml
```
### Calculate ROI
Batch process that calculates ROI of the trading model based on the online predictions. It reads predictions from elastic (`prediction` index) as writes it to other index - `roi`
```bash
PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process calculate_roi
```