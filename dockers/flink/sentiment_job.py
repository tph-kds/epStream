from pyflink.table import TableEnvironment, EnvironmentSettings

def sink_to_elasticsearch(t_env: TableEnvironment):
    # register Elasticsearch sink
    t_env.execute_sql("""
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
    'hosts' = 'http://elasticsearch:9200',
    'index' = 'comments_logs',
    'document-id' = 'comment_id',
    'format' = 'json'
    )
    """)

    t_env.execute_sql("""
    INSERT INTO comments_es
    SELECT * FROM comments_processed
    """)

    print("Elasticsearch sink registered and data inserted successfully.")

def sink_to_postgres(t_env: TableEnvironment):
    # register Postgres sink
    t_env.execute_sql("""
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
    'url' = 'jdbc:postgresql://postgres:5432/eps',
    'table-name' = 'comments',
    'username' = 'eps',
    'password' = 'eps',
    'driver' = 'org.postgresql.Driver'
    )
    """)

    # insert into Postgres
    t_env.execute_sql("""
    INSERT INTO comments_pg
    SELECT * FROM comments_processed
    """)    
    print("Postgres sink registered and data inserted successfully.")

def main():
    env_settings = EnvironmentSettings.in_streaming_mode()
    table_env = TableEnvironment.create(env_settings)

    print("Flink job setup complete. Starting execution...")
    # Sink to Postgres
    sink_to_postgres(table_env)
    # Sink to Elasticsearch
    sink_to_elasticsearch(table_env)
    print("Flink job execution completed.")




if __name__ == "__main__":
    main()
