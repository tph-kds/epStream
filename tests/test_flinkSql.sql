CREATE TABLE comments_raw (
   comment_id STRING,
   text STRING,
   ts_event_utc TIMESTAMP(3)
) WITH (
   'connector' = 'kafka',
   'topic' = 'comments_raw',
   'properties.bootstrap.servers' = 'kafka:9092',
   'format' = 'json'
);

SELECT * FROM comments_raw;