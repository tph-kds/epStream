import os, json 
from dotenv import load_dotenv
from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table.udf import udf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pyflink.common import Configuration


load_dotenv()

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

def main():
    settings = EnvironmentSettings.in_streaming_mode()
    table_env = TableEnvironment.create(settings)

    # table_env.get_config().set("pipeline.classpaths", "file:///opt/flink/lib/custom_elasticsearch_client/elasticsearch-7.17.29.jar;file:///opt/flink/lib/custom_elasticsearch_client/elasticsearch-rest-high-level-client-7.17.29.jar")


    broker = os.getenv("KAFKA_BROKER", "broker:29092")
    topic_in = os.getenv("KAFKA_TOPIC", "tiktok_comments")
    topic_out = os.getenv("KAFKA_TOPIC_PROCESSED", "tiktok_comments_enriched")
    es_host = os.getenv("ES_HOST", "http://es-container:9200")
    es_index = os.getenv("ES_INDEX", "tiktok_comments")
    postgres_url = os.getenv("POSTGRES_URL", "jdbc:postgresql://postgres:5432/airflow")
    postgres_user = os.getenv("POSTGRES_USER", "airflow")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "airflow")

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
      ts_event_utc_ms BIGINT,
      ts_event_utc AS TO_TIMESTAMP_LTZ(ts_event_utc_ms, 3),
      WATERMARK FOR ts_event_utc AS ts_event_utc - INTERVAL '5' SECOND,
      ts_event TIMESTAMP(3)
    ) WITH (
      'connector' = 'kafka',
      'topic' = '{topic_in}',
      'properties.bootstrap.servers' = '{broker}',
      'properties.group.id' = 'flink-consumer',
      'scan.startup.mode' = 'earliest-offset',
      'format' = 'json',
      'json.ignore-parse-errors' = 'true',
      'sink.partitioner' = 'fixed',
      'sink.transactional-id-prefix' = 'kafka-flink-comments_raw',
      'sink.parallelism' = '1'
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
      ts_event_utc TIMESTAMP_LTZ(3),
      sentiment_score DOUBLE,
      sentiment_label STRING
    ) WITH (
      'connector' = 'kafka',
      'topic' = '{topic_out}',
      'properties.bootstrap.servers' = '{broker}',
      'format' = 'json',
      'json.timestamp-format.standard' = 'ISO-8601',
      'sink.partitioner' = 'fixed',
      'sink.transactional-id-prefix' = 'kafka-flink-comments_processed',
      'sink.parallelism' = '1'
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
      sentiment_label STRING,
      PRIMARY KEY (comment_id) NOT ENFORCED
    ) WITH (
      'connector' = 'jdbc',
      'url' = '{postgres_url}',
      'table-name' = 'public.comments',
      'username' = '{postgres_user}',
      'password' = '{postgres_password}',
      'driver' = 'org.postgresql.Driver',
      'sink.parallelism' = '1'
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
      ts_event TIMESTAMP(3),
      sentiment_score DOUBLE,
      sentiment_label STRING,
      PRIMARY KEY (comment_id) NOT ENFORCED
    ) WITH (
      'connector' = 'elasticsearch-7',
      'hosts' = '{es_host}',
      'index' = '{es_index}',
      'document-id.key-delimiter' = '_',
      'sink.bulk-flush.max-actions' = '1000',
      'sink.bulk-flush.interval' = '2s',
      'format' = 'json'
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
    kafka_insert_table = """
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
    """

    # ----------------------------
    # Insert into Postgres
    # ----------------------------
    postgres_insert_table = """
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
    """

    # ----------------------------
    # Insert into Elasticsearch
    # ----------------------------
    elasticsearch_insert_table = """
    INSERT INTO comments_es
    SELECT
        comment_id,
        platform,
        stream_id,
        user_id,
        username,
        text,
        lang,
        ts_event,
        score_sentiment(text),
        label_sentiment(text)
    FROM comments_raw
    """

    # ================================
    # 5. STATEMENT SET
    # ================================
    stmt_set = table_env.create_statement_set()
    stmt_set.add_insert_sql(kafka_insert_table)
    stmt_set.add_insert_sql(postgres_insert_table)
    stmt_set.add_insert_sql(elasticsearch_insert_table)

    stmt_set.execute()


if __name__ == "__main__":
    main()
    # Submit Job
        #     docker exec -it flink-jobmanager bash -lc \
        #   "pip install apache-flink vaderSentiment && python /opt/processor/flink_job.py"