#!/bin/bash

PYSPARK_PYTHON=./venv/bin/python spark-submit --master local[*] main.py --process online_ml &> online.log &


/bin/bash << EOT &
while true; do
    PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process news_to_redis
    sleep 60
done
EOT


/bin/bash << EOT &
while true; do
    PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process calculate_roi
    sleep 60
done
EOT

/bin/bash << EOT &
while true; do
    PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process logs_to_elastic
    sleep 60
done
EOT