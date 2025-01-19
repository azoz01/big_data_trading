#!/bin/bash

PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process online_ml &> online.log &


/bin/bash << EOT &
while true; do
    PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process news_to_redis
    sleep 60
done
EOT
