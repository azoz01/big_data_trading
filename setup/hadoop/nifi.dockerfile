FROM apache/nifi:1.28.0

RUN curl -fo /opt/nifi/nifi-current/lib/nifi-hadoop-nar-1.28.0.nar https://repo1.maven.org/maven2/org/apache/nifi/nifi-hadoop-nar/1.28.0/nifi-hadoop-nar-1.28.0.nar

COPY config/hdfs-site.xml /opt/config/
COPY config/core-site.xml /opt/config/

ENTRYPOINT ["../scripts/start.sh"]