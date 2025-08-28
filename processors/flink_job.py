from __future__ import annotations

import os
from dotenv import load_dotenv
from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table.udf import udf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ----------------------------
# Load env variables
# ----------------------------
load_dotenv()

BROKER = os.getenv("KAFKA_BROKER", "broker:29092")
TOPIC_IN = os.getenv("KAFKA_TOPIC", "tiktok_comments")
TOPIC_OUT = os.getenv("KAFKA_TOPIC_PROCESSED", "tiktok_comments_processed")
POSTGRES_URL = os.getenv("POSTGRES_URL", "jdbc:postgresql://postgres:5432/airflow")
POSTGRES_USER = os.getenv("POSTGRES_USER", "airflow")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
ES_INDEX = os.getenv("ES_INDEX", "comments")

# ----------------------------
# Sentiment UDFs
# ----------------------------
analyzer = SentimentIntensityAnalyzer()

@udf(result_type='STRING')
def label_sentiment(text: str) -> str:
    if not text:
        return "neutral"
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"

@udf(result_type='DOUBLE')
def score_sentiment(text: str) -> float:
    if not text:
        return 0.0
    return float(analyzer.polarity_scores(text)['compound'])

# ----------------------------
# Main Flink Job
# ----------------------------
def main():
    # Create streaming TableEnvironment
    settings = EnvironmentSettings.in_streaming_mode()
    table_env = TableEnvironment.create(settings)

    # ----------------------------
    # Source: Kafka JSON
    # ----------------------------
    table_env.execute_sql(f"""
    CREATE TABLE comments_raw (
      comment_id STRING,
      platform STRING,
      stream_id STRING,
      user_id STRING,
      username STRING,
      text STRING,
      lang STRING,
      ts_event_utc TIMESTAMP(3),
      WATERMARK FOR ts_event_utc AS ts_event_utc - INTERVAL '5' SECOND
    ) WITH (
      'connector' = 'kafka',
      'topic' = '{TOPIC_IN}',
      'properties.bootstrap.servers' = '{BROKER}',
      'properties.group.id' = 'flink-consumer',
      'scan.startup.mode' = 'latest-offset',
      'format' = 'json',
      'json.ignore-parse-errors' = 'true'
    )
    """)

    # ----------------------------
    # Sink 1: Kafka processed
    # ----------------------------
    table_env.execute_sql(f"""
    CREATE TABLE comments_processed (
      comment_id STRING,
      platform STRING,
      stream_id STRING,
      user_id STRING,
      username STRING,
      text STRING,
      lang STRING,
      ts_event_utc TIMESTAMP(3),
      sentiment_score DOUBLE,
      sentiment_label STRING
    ) WITH (
      'connector' = 'kafka',
      'topic' = '{TOPIC_OUT}',
      'properties.bootstrap.servers' = '{BROKER}',
      'format' = 'json',
      'json.timestamp-format.standard' = 'ISO-8601'
    )
    """)

    # ----------------------------
    # Sink 2: Postgres
    # ----------------------------
    table_env.execute_sql(f"""
    CREATE TABLE comments_pg (
      comment_id STRING,
      platform STRING,
      stream_id STRING,
      user_id STRING,
      username STRING,
      text STRING,
      lang STRING,
      ts_event_utc TIMESTAMP(3),
      sentiment_score DOUBLE,
      sentiment_label STRING
    ) WITH (
      'connector' = 'jdbc',
      'url' = '{POSTGRES_URL}',
      'table-name' = 'comments',
      'username' = '{POSTGRES_USER}',
      'password' = '{POSTGRES_PASSWORD}',
      'driver' = 'org.postgresql.Driver'
    )
    """)

    # ----------------------------
    # Sink 3: Elasticsearch
    # ----------------------------
    table_env.execute_sql(f"""
    CREATE TABLE comments_es (
      comment_id STRING,
      platform STRING,
      stream_id STRING,
      user_id STRING,
      username STRING,
      text STRING,
      lang STRING,
      ts_event_utc TIMESTAMP(3),
      sentiment_score DOUBLE,
      sentiment_label STRING
    ) WITH (
      'connector' = 'elasticsearch-7',
      'hosts' = '{ES_HOST}',
      'index' = '{ES_INDEX}',
      'document-id.key-delimiter' = '-',
      'document-id.key.fields' = 'comment_id'
    )
    """)

    # ----------------------------
    # Register UDFs
    # ----------------------------
    table_env.create_temporary_system_function("label_sentiment", label_sentiment)
    table_env.create_temporary_system_function("score_sentiment", score_sentiment)

    # ----------------------------
    # Insert into Kafka
    # ----------------------------
    table_env.execute_sql("""
    INSERT INTO comments_processed
    SELECT
        comment_id,
        platform,
        stream_id,
        user_id,
        username,
        text,
        lang,
        ts_event_utc,
        score_sentiment(text) AS sentiment_score,
        label_sentiment(text) AS sentiment_label
    FROM comments_raw
    """)

    # ----------------------------
    # Insert into Postgres
    # ----------------------------
    table_env.execute_sql("""
    INSERT INTO comments_pg
    SELECT
        comment_id,
        platform,
        stream_id,
        user_id,
        username,
        text,
        lang,
        ts_event_utc,
        score_sentiment(text),
        label_sentiment(text)
    FROM comments_raw
    """)

    # ----------------------------
    # Insert into Elasticsearch
    # ----------------------------
    table_env.execute_sql("""
    INSERT INTO comments_es
    SELECT
        comment_id,
        platform,
        stream_id,
        user_id,
        username,
        text,
        lang,
        ts_event_utc,
        score_sentiment(text),
        label_sentiment(text)
    FROM comments_raw
    """)

if __name__ == "__main__":
    main()
# ----------------------------
