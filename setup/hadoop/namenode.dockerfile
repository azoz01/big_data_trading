FROM apache/hadoop:3

RUN wget https://dlcdn.apache.org/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz
RUN wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar
RUN wget https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz --no-check-certificate
RUN sudo curl -o /etc/yum.repos.d/CentOS-Base.repo https://el7.repo.almalinux.org/centos/CentOS-Base.repo
# RUN sudo yum install -y python3.9
RUN sudo yum install -y gcc sqlite-devel openssl-devel bzip2-devel libffi-devel zlib-devel make \
    && cd /tmp \
    && wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz \
    && tar -xvf Python-3.9.6.tgz \
    && cd Python-3.9.6 \
    && ./configure --enable-optimizations \
    && sudo make altinstall

# SETUP HIVE
# hive
RUN tar zxvf apache-hive-4.0.1-bin.tar.gz \
    && mv apache-hive-4.0.1-bin /opt/hive \
    && rm apache-hive-4.0.1-bin.tar.gz

# metastore connector
RUN mv mysql-connector-java-8.0.28.jar /opt/hive/lib/

# setup metastore
ENV HIVE_HOME=/opt/hive
ENV PATH=$PATH:$HIVE_HOME/bin
COPY setup/hadoop/config/hive-site.xml /opt/hive/conf/
COPY setup/hadoop/config/core-site.xml /opt/hive/conf/

# SETUP SPARK

RUN mkdir /opt/spark
RUN mv spark-3.4.0-bin-hadoop3.tgz /opt/spark/
RUN tar -zxvf /opt/spark/spark-3.4.0-bin-hadoop3.tgz -C /opt/spark
RUN cp /opt/hive/lib/mysql-connector-java-8.0.28.jar /opt/spark/spark-3.4.0-bin-hadoop3/jars/
RUN curl -fo /opt/spark/spark-3.4.0-bin-hadoop3/jars/spark-sql-kafka-0-10_2.12-3.4.0.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.4.0/spark-sql-kafka-0-10_2.12-3.4.0.jar
RUN curl -fo /opt/spark/spark-3.4.0-bin-hadoop3/jars/kafka-clients-3.9.0.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.9.0/kafka-clients-3.9.0.jar
RUN curl -fo /opt/spark/spark-3.4.0-bin-hadoop3/jars/spark-token-provider-kafka-0-10_2.12-3.4.0.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.4.0/spark-token-provider-kafka-0-10_2.12-3.4.0.jar
RUN curl -fo /opt/spark/spark-3.4.0-bin-hadoop3/jars/commons-pool2-2.12.0.jar \
    https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.12.0/commons-pool2-2.12.0.jar
RUN curl -fo /opt/spark/spark-3.4.0-bin-hadoop3/jars/jedis-3.9.0.jar \
    https://repo1.maven.org/maven2/redis/clients/jedis/3.9.0/jedis-3.9.0.jar
RUN curl -fo /opt/spark/spark-3.4.0-bin-hadoop3/jars/spark-redis_2.12-3.1.0.jar \
https://repo1.maven.org/maven2/com/redislabs/spark-redis_2.12/3.1.0/spark-redis_2.12-3.1.0.jar
RUN curl -fo /opt/spark/spark-3.4.0-bin-hadoop3/jars/elasticsearch-spark-30_2.12-8.15.3.jar \
    https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-30_2.12/8.15.3/elasticsearch-spark-30_2.12-8.15.3.jar

RUN sudo ln -s /usr/local/bin/python3.9 /usr/bin/python3
ENV PATH="$PATH:/opt/spark/spark-3.4.0-bin-hadoop3/bin"

WORKDIR /code
RUN python3.9 -m venv venv
COPY code/requirements.txt .
RUN ./venv/bin/pip install -r requirements.txt
COPY code .

RUN cp /opt/hive/conf/hive-site.xml /opt/spark/spark-3.4.0-bin-hadoop3/conf/
COPY setup/hadoop/config/spark-defaults.conf /opt/spark/spark-3.4.0-bin-hadoop3/conf/