from typing import Any, Dict, List 
import os, json, time, uuid
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

from .data_collectors import (
    MultiPlatformData,
    MultiPlatformDataConfig
)
from .cli_init import CliInitialization
from utils import (
    JsonFile,
    JsonFileConfig
)

from datetime import datetime, timezone
from dotenv import load_dotenv
from kafka import KafkaProducer
from .schema import CommentSchema, CliConfig

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

    comments_dict = comments_data.model_dump()
    print(f"comments_dict: {comments_dict["ts_events"]}")
    print(f"comments_dict: {comments_dict["comment_ids"]}")
    print(f"comments_dict: {comments_dict['platforms']}")
    print(f"comments_dict: {comments_dict['stream_ids']}")
    print(f"comments_dict: {comments_dict['user_ids']}")
    print(f"comments_dict: {comments_dict['usernames']}")
    print(f"comments_dict: {comments_dict['texts']}")
    print(f"comments_dict: {comments_dict['comments']}")
    print(f"comments_dict: {comments_dict['langs']}")
    print(f"comments_dict: {comments_dict['ts_event_utc_mss']}")
    print(f"comments_dict: {comments_dict['ts_events']}")

    return [
        CommentSchema(
            comment_id=cid,
            platform=plat,
            stream_id=sid,
            user_id=uid,
            username=uname,
            # text=text,
            comment=comment,
            lang=lang,
            ts_event_utc_ms=ts_ms,
            ts_event=ts
        ).model_dump()
        for cid, plat, sid, uid, uname, comment, lang, ts_ms, ts
        in zip(
            comments_dict["comment_ids"],
            comments_dict["platforms"],
            comments_dict["stream_ids"],
            comments_dict["user_ids"],
            comments_dict["usernames"],
            # comments_dict.get("texts", []),  # safe optional
            comments_dict.get("comments", []),  # safe optional
            comments_dict["langs"],
            comments_dict["ts_event_utc_mss"],
            comments_dict["ts_events"],
        )
    ]


def init_cli_args():
    parser = CliInitialization(CliConfig(
        description="Test fetch and cleaned comments from user input"
    ))
    args = parser.parse_args_cli()
    return args


def main(comments: List[CommentSchema] = None):
    for i in range(2):
        with tracer.start_as_current_span("fetch_comments"):
            for comment in comments:
                c = CommentSchema(**comment)
                producer.send(TOPIC, value=c.model_dump())
                logger.info(f"=------------------Message {i + 1}------------------=")
                logger.info(f"Sent comment to Kafka: {c.model_dump()}")
                logger.info(f"Current span context: {trace.get_current_span().get_span_context()}")

        producer.flush()
        time.sleep(2)


def init():
    args = init_cli_args()
    print(f"args: {args}")
    print(f"args.mock: {args.mock}")
    dict_inputs = {
        "platform": args.platform,
        "host_id": args.host_id,
        "number_of_comments": args.number_of_comments,
        "events": args.events,
        "client_name": args.client_name
    }

    inputs = {
        "platform": args.platform,
        "tiktok_platform_config": dict_inputs if args.platform == "tiktok" else None,
        "youtube_platform_config": dict_inputs if args.platform == "youtube" else None,
        "facebook_platform_config": dict_inputs if args.platform == "facebook" else None,
    }
    print(f"Inputs: \n {inputs} \n")
    if args.mock:
        comments = mock_fetch_comments()
    
    else:
        comments = fetch_and_cleaned_comments(inputs)
    
    if args.output:
        source_path = args.output.split("/")[:-1]
        file_name = args.output.split("/")[-1]
        json_config = JsonFileConfig(source_path=source_path, file_name=file_name)
        json_file = JsonFile(json_config=json_config)
        json_file.save_json({"comments_data": comments})

        print(f"File Json containing comments saved at: {json_file.file_path}")
    
    return comments


if __name__ == "__main__":
    try:
        comments = init()
        main(comments=comments)
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
        