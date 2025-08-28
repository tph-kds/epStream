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

echo "✅ All JARs are now in ${FLINK_LIB_DIR}"
ls -lh ${FLINK_LIB_DIR}
