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
    cd setup && ./initialize_host.sh && ./run.sh
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