#!/bin/bash
set -e

docker build --progress plain -t azoz01/hadoop-namenode -f setup/hadoop/namenode.dockerfile .
docker build --progress plain -t azoz01/nifi -f setup/hadoop/nifi.dockerfile .

docker compose --file setup/hadoop/docker-compose.yaml up