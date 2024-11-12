## Setup
Before running docker compose you need to run following commands:
```
sudo sysctl -w vm.max_map_count=262144
useradd hadoop
groupadd hadoop
sudo usermod -aG hadoop hadoop
```

Also, you need to have docker and docker compose installed.

To start run entire setup execute:
``` bash
    cd setup && ./initialize_host.sh && ./run.sh
```

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