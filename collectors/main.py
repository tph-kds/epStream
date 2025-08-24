import os, json, time, uuid

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
span_prossesor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")),
    in_secure=True,
)

trace.get_tracer_provider().add_span_processor(span_prossesor)
tracer = trace.get_tracer(os.getenv("OTEL_SERVICE_NAME", "tiktok-collector"))

BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "tiktok_comments")

producer = KafkaProducer(
    bootstrap_servers = BROKER,
    value_serializer = lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)

def mock_fetch_comments():
    comments_data = []
    return [{
        "comment_id": str(uuid.uuid4()),
        "stream_id": "stream-001",
        "username": "user123",
        "text": "This live is awesome!",
        "ts_event_utc": datetime.now(timezone.utc).isoformat()
    }]



def main():
    while True:
        with tracer.start_as_current_span("fetch_comments"):
            comments = mock_fetch_comments()
            for comment in comments:
                c = CommentSchema(**comment)
                producer.send(TOPIC, value=c.model_dump())
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
        span_prossesor.shutdown()
        print("Span processor shutdown.")
        trace.get_tracer_provider().shutdown()
        print("Tracer provider shutdown.")
        print("OpenTelemetry shutdown complete.")
        print("Exiting collector.")
        