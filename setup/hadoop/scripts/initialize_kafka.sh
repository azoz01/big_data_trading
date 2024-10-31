#!/bin/bash

/opt/kafka/bin/kafka-topics.sh  --bootstrap-server kafka:9092 --create --if-not-exists --topic test-topic