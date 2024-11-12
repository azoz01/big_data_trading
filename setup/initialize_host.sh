#!/bin/bash

umask 000

mkdir -p ../data/hadoop
mkdir -p ../data/hive
mkdir -p ../data/elastic
mkdir -p ../data/nifi/database_repository
mkdir -p ../data/nifi/flowfile_repository
mkdir -p ../data/nifi/content_repository
mkdir -p ../data/nifi/provenance_repository
mkdir -p ../data/nifi/state
mkdir -p ../data/nifi/logs


sudo chown hadoop:hadoop ../data/hadoop
sudo chown hadoop:hadoop ../data/hive
sudo chmod -R 777 ../data