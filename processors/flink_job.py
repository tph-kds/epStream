import os, json 
from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table.udf import udf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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
    settings = EnvironmentSettings.in_streaming_mode().use_blink_planner().build()
    table_env = TableEnvironment.create(settings)

    broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    topic_in = os.getenv("KAFKA_TOPIC", "tiktok_comments")
    topic_out = os.getenv("KAFKA_TOPIC_PROCESSED", "tiktok_comments_enriched")

    # Source Kafka (JSON)
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
      'topic' = '{topic_in}',
      'properties.bootstrap.servers' = '{broker}',
      'properties.group.id' = 'flink-consumer',
      'scan.startup.mode' = 'latest-offset',
      'format' = 'json',
      'json.ignore-parse-errors' = 'true'
    )
    """)

        # Sink Kafka processed
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
      'topic' = '{topic_out}',
      'properties.bootstrap.servers' = '{broker}',
      'format' = 'json',
      'json.timestamp-format.standard' = 'ISO-8601'
    )
    """)

    table_env.create_temporary_system_function("label_sentiment", label_sentiment)
    table_env.create_temporary_system_function("score_sentiment", score_sentiment)

    table_env.execute_sql("""
      INSERT INTO comments_processed
      SELECT
        comment_id, platform, stream_id, user_id, username, text, lang, ts_event_utc,
        score_sentiment(text) AS sentiment_score,
        label_sentiment(text) AS sentiment_label
      FROM comments_raw
    """)


if __name__ == "__main__":
    main()
    # Submit Job
        #     docker exec -it flink-jobmanager bash -lc \
        #   "pip install apache-flink vaderSentiment && python /opt/processor/flink_job.py"