FROM apache/nifi:1.28.0

RUN curl -fo /opt/nifi/nifi-current/lib/nifi-hadoop-nar-1.28.0.nar https://repo1.maven.org/maven2/org/apache/nifi/nifi-hadoop-nar/1.28.0/nifi-hadoop-nar-1.28.0.nar

COPY config/blockchain.pem /opt/config/
COPY config/digicert.pem /opt/config/
RUN keytool -genkey -alias nifi-cert -keyalg RSA -keystore /opt/nifi/keystore.jks -keysize 2048 -storepass passpass -dname "cn=bigdata"
RUN keytool -import -trustcacerts -file /opt/config/blockchain.pem -alias blockchain-websocket -keystore /opt/nifi/truststore.jks -storepass passpass -noprompt
RUN keytool -import -trustcacerts -file /opt/config/digicert.pem -alias digicert -keystore /opt/nifi/truststore.jks -storepass passpass -noprompt

COPY config/hdfs-site.xml /opt/config/
COPY config/core-site.xml /opt/config/

ENTRYPOINT ["../scripts/start.sh"]