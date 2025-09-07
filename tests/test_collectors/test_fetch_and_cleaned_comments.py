from typing import Any, Dict
import os, json, time, uuid
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

from collectors.data_collectors import (
    MultiPlatformData,
    MultiPlatformDataConfig
)
from collectors import CliInitialization

from datetime import datetime, timezone
from collectors.schema import CommentSchema, CliConfig
from dotenv import load_dotenv



load_dotenv()


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


if __name__ == "__main__":
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

    print(comments)

# @bobim.pubgm
# @bacgau1989
# @nhotv12345
# uv run tests/test_collectors/test_fetch_and_cleaned_comments.py -p tiktok -hi @bobim.pubgm -nc 10 -cn tiktok_client