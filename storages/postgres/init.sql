CREATE TABLE IF NOT EXISTS comments (
    comment_id VARCHAR PRIMARY KEY,
    platform VARCHAR NOT NULL,
    stream_id VARCHAR NOT NULL,
    user_id VARCHAR,
    username VARCHAR,
    text TEXT NOT NULL,
    language VARCHAR(10),
    ts_event_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(20),
    ingested_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_comments_stream_ts 
ON comments (stream_id, ts_event_utc DESC);