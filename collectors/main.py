from typing import Any, Dict
import os, json, time, uuid
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

from data_collectors import (
    MultiPlatformData,
    MultiPlatformDataConfig
)

from datetime import datetime, timezone
from dotenv import load_dotenv
from kafka import KafkaProducer
from schema import CommentSchema

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

load_dotenv()
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector:4317"),
    insecure=True  # ✅ để kết nối gRPC không TLS
)

span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)
tracer = trace.get_tracer(os.getenv("OTEL_SERVICE_NAME", "tiktok-collector"))

BROKER = os.getenv("KAFKA_BROKER", "broker:29092")
TOPIC = os.getenv("KAFKA_TOPIC", "tiktok_comments")


def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

producer = KafkaProducer(
    bootstrap_servers = BROKER,
    value_serializer = lambda v: json.dumps(v, ensure_ascii=False, default=json_serializer).encode("utf-8"),
)

def mock_fetch_comments():
    comments_data = []
    return [{
        "comment_id": str(uuid.uuid4()),
        "platform": "tiktok",
        "stream_id": "stream-001",
        "user_id": "utest-" + str(uuid.uuid4())[:8],
        "username": "user_test__" + str(uuid.uuid4())[:5],
        "text": "This live is awesome!",
        "lang": "en",
        "ts_event_utc_ms": int(datetime.now(timezone.utc).timestamp() * 1000),
        "ts_event": datetime.now(timezone.utc).isoformat()
    }]

def fetch_and_cleaned_comments(inputs: Dict[str, Any]) -> CommentSchema:
    # Fetch comments from the target platform such as TikTok, YouTube, Facebook
    multiplatform_data = MultiPlatformData(
        mpd_config=MultiPlatformDataConfig(
            platform = inputs["platform"],
            tiktok_platform_config=inputs["tiktok_platform_config"],
            youtube_platform_config=inputs["youtube_platform_config"],
            facebook_platform_config=inputs["facebook_platform_config"]
        ),
    )

    comments_data = multiplatform_data.run_data_collection()

    return [CommentSchema(**comment) for comment in comments_data]

def main():
    for i in range(2):
        with tracer.start_as_current_span("fetch_comments"):
            comments = mock_fetch_comments()
            for comment in comments:
                c = CommentSchema(**comment)
                producer.send(TOPIC, value=c.model_dump())
                logger.info(f"=------------------Message {i + 1}------------------=")
                logger.info(f"Sent comment to Kafka: {c.model_dump()}")
                logger.info(f"Current span context: {trace.get_current_span().get_span_context()}")

        producer.flush()
        time.sleep(2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Collector stopped by user.")
    finally:
        producer.close()
        print("Kafka producer closed.")
        span_processor.shutdown()
        print("Span processor shutdown.")
        trace.get_tracer_provider().shutdown()
        print("Tracer provider shutdown.")
        print("OpenTelemetry shutdown complete.")
        print("Exiting collector.")
        