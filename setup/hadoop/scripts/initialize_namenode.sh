#!/bin/bash

# SETUP HADOOP
sudo chown hadoop:hadoop /tmp/hadoop-hadoop/dfs/name

export VERSION_PATH="/tmp/hadoop-hadoop/dfs/name/current/VERSION"
if ! [ -f $VERSION_PATH ]; then
    hdfs namenode -format -force
fi

hadoop namenode &

hadoop fs -mkdir -p /tmp/hive
hadoop fs -mkdir -p /user/hive/warehouse
sleep 1
hadoop fs -chmod 777 /tmp
hadoop fs -chmod 777 /user/hive/warehouse

if [[ $(schematool -info -dbType mysql 2>/dev/null | grep -c "Metastore schema version:") -eq 0 ]]; then
    schematool -initSchema -dbType mysql --verbose 
fi
hive --service hiveserver2