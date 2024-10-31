FROM apache/hadoop:3

RUN wget https://dlcdn.apache.org/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz
RUN wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar
RUN wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz --no-check-certificate
RUN wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz
RUN sudo curl -o /etc/yum.repos.d/CentOS-Base.repo https://el7.repo.almalinux.org/centos/CentOS-Base.repo
RUN sudo yum install -y python3

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
COPY ./config/hive-site.xml /opt/hive/conf/

# SETUP SPARK

RUN mkdir /opt/spark
RUN mv spark-3.5.0-bin-hadoop3.tgz /opt/spark/
RUN tar -zxvf /opt/spark/spark-3.5.0-bin-hadoop3.tgz -C /opt/spark
RUN cp /opt/hive/lib/mysql-connector-java-8.0.28.jar /opt/spark/spark-3.5.0-bin-hadoop3/jars/

RUN sudo unlink /usr/bin/python && sudo ln -s /usr/bin/python3 /usr/bin/python