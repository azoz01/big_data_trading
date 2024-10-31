#!/bin/bash

umask 000

mkdir -p ../data/hadoop
mkdir -p ../data/hive
mkdir -p ../data/elastic

sudo chown hadoop:hadoop ../data/hadoop 
sudo chown hadoop:hadoop ../data/hive
sudo chmod -R 777 ../data