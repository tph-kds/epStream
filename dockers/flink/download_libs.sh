#!/bin/bash
set -e

echo "🔽 Downloading Flink connectors & drivers..."

# Move into Flink lib folder
cd /opt/flink/lib

if [ ! -f flink-connector-jdbc-3.3.0-1.20.jar ]; then
  # JDBC Connector
  wget -q -O flink-connector-jdbc-3.3.0-1.20.jar \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.3.0-1.20/flink-connector-jdbc-3.3.0-1.20.jar
fi

if [ ! -f postgresql-42.7.7.jar ]; then
  # PostgreSQL Driver
  wget -q -O postgresql-42.7.7.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.7/postgresql-42.7.7.jar
fi

if [ ! -f flink-connector-kafka-4.0.1-2.0.jar ]; then
  # Kafka Connector
  wget -q -O flink-connector-kafka-4.0.1-2.0.jar \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/4.0.1-2.0/flink-connector-kafka-4.0.1-2.0.jar
fi

echo "✅ All JARs downloaded into /opt/flink/lib/"
ls -lh /opt/flink/lib/






# env.add_jars(
#   f"file://{current_dir}/flink-connector-jdbc-3.3.0-1.20.jar",
#   f"file://{current_dir}/postgresql-42.7.7.jar",
#   f"file://{current_dir}/flink-connector-kafka-4.0.1-2.0.jar",
# )

# # How to download entire files jars
# # # Flink Kafka Connector (4.0.1-2.0 for Flink 2.0.x)
# wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/4.0.1-2.0/flink-connector-kafka-4.0.1-2.0.jar -P ./dockers/flink/lib/

# # Flink JDBC Connector (3.3.0-1.20 for Flink 1.20.x)
# wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.3.0-1.20/flink-connector-jdbc-3.3.0-1.20.jar -P ./dockers/flink/lib/

# # PostgreSQL Driver (42.7.7 là mới nhất ổn định)
# wget https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.7/postgresql-42.7.7.jar -P ./dockers/flink/lib/