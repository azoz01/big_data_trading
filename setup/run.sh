#!/bin/bash
set -e

cd hadoop
docker build --progress plain -t azoz01/hadoop-namenode -f namenode.dockerfile .
docker build --progress plain -t azoz01/nifi -f nifi.dockerfile .

cd ..
docker compose up