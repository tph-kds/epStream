#!/bin/bash
set -e

FLINK_LIB_DIR="/opt/flink/lib"

echo "🔽 Downloading Flink connectors & drivers into ${FLINK_LIB_DIR} ..."
mkdir -p ${FLINK_LIB_DIR}
cd ${FLINK_LIB_DIR}

# JDBC Connector
if [ ! -f flink-connector-jdbc-core-4.0.0-2.0.jar ]; then
  wget -q -O flink-connector-jdbc-core-4.0.0-2.0.jar \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc-core/4.0.0-2.0/flink-connector-jdbc-core-4.0.0-2.0.jar
fi

# PostgreSQL Driver
if [ ! -f postgresql-42.7.7.jar ]; then
  wget -q -O postgresql-42.7.7.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.7/postgresql-42.7.7.jar
fi

# Flink SQL JDBC Driver Bundle
if [ ! -f flink-sql-jdbc-driver-bundle-2.0.0.jar ]; then
  wget -q -O flink-sql-jdbc-driver-bundle-2.0.0.jar \
    https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-jdbc-driver-bundle/2.0.0/flink-sql-jdbc-driver-bundle-2.0.0.jar
fi

if [ ! -f flink-connector-jdbc-postgres-4.0.0-2.0.jar ]; then
  wget -q -O flink-connector-jdbc-postgres-4.0.0-2.0.jar \
    https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-jdbc-postgres/4.0.0-2.0/flink-connector-jdbc-postgres-4.0.0-2.0.jar
fi

# # ElasticSearch7 Connector
# if [ ! -f flink-connector-elasticsearch7-4.0.0-2.0.jar ]; then
#   wget -q -O flink-connector-elasticsearch7-4.0.0-2.0.jar \
#     https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-elasticsearch7/4.0.0-2.0/flink-connector-elasticsearch7-4.0.0-2.0.jar
# fi
# SQL ElasticSearch7 Connector
if [ ! -f flink-sql-connector-elasticsearch7-4.0.0-2.0.jar ]; then
  wget -q -O flink-sql-connector-elasticsearch7-4.0.0-2.0.jar \
    https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch7/4.0.0-2.0/flink-sql-connector-elasticsearch7-4.0.0-2.0.jar
fi
# # ElasticSearch Client
# if [ ! -f elasticsearch-rest-high-level-client-7.17.28.jar ]; then
#   wget -q -O elasticsearch-rest-high-level-client-7.17.28.jar \
#     https://repo1.maven.org/maven2/org/elasticsearch/client/elasticsearch-rest-high-level-client/7.17.28/elasticsearch-rest-high-level-client-7.17.28.jar
# fi

# if [ ! -f elasticsearch-7.17.28.jar ]; then
#   wget -q -O elasticsearch-7.17.28.jar \
#     https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch/7.17.28/elasticsearch-7.17.28.jar
# fi


# Kafka Connector
if [ ! -f flink-connector-kafka-4.0.0-2.0.jar ]; then
  wget -q -O flink-connector-kafka-4.0.0-2.0.jar \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/4.0.0-2.0/flink-connector-kafka-4.0.0-2.0.jar
fi

# Kafka Client
if [ ! -f kafka-clients-4.0.0.jar ]; then
  wget -q -O kafka-clients-4.0.0.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/4.0.0/kafka-clients-4.0.0.jar
fi



# -----------------------------
# Zip Elasticsearch client jars
# -----------------------------
# CUSTOM_ES_DIR="${FLINK_LIB_DIR}/custom_elasticsearch_client"
# mkdir -p ${CUSTOM_ES_DIR}

# cp elasticsearch-rest-high-level-client-7.17.29.jar elasticsearch-7.17.29.jar ${CUSTOM_ES_DIR}
# ------------------------------------------------------------
# zip -r custom_elasticsearch_client.zip custom_elasticsearch_client

# Delete temporary directory and original files
# rm -rf custom_elasticsearch_client
# ----------------------------------------------

# rm -f elasticsearch-rest-high-level-client-7.17.29.jar elasticsearch-7.17.29.jar

# echo "✅ Elasticsearch client jars zipped at ${FLINK_LIB_DIR}/custom_elasticsearch_client.zip"
# -------------------------------------------------
echo "✅ All JARs are now in ${FLINK_LIB_DIR}"
ls -lh ${FLINK_LIB_DIR}
# if [ ! -f elasticsearch-rest-client-7.17.29.jar ]; then
#   wget -q -O elasticsearch-rest-client-7.17.29.jar \
#     https://repo1.maven.org/maven2/org/elasticsearch/client/elasticsearch-rest-client/7.17.29/elasticsearch-rest-client-7.17.29.jar
# fi