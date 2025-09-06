from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, List, Optional

class CommentSchema(BaseModel):
    comment_id: str = Field(..., description="Unique identifier for the comment")
    platform: str = Field(..., description="Platform where the comment was made (e.g., TikTok)")
    stream_id: str = Field(..., description="Unique identifier for the stream")

    user_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the user who made the comment"
    )
    username: Optional[str] = Field(
        default=None,
        description="Username of the user who made the comment"
    )
    comment : Optional[str] = Field(
        default=None,
        description="The cleaned text content of the comment"
    )
    text: Optional[str] = Field(
        default=None,
        description="The original text content of the comment",
        min_length=1
    )
    language: Optional[str] = Field(
        default=None,
        description="Language of the comment text"
    )
    ts_event_utc_ms: int = Field(
        ...,
        description="Timestamp of the event in UTC (milliseconds)",
        example=1696156800000
    )


class CliConfig(BaseModel):
    description: Optional[str] = Field(
        default="Data collector for live stream comments",
        description="Description of the data collector"
    )

    # keywords: Optional[List[str]] = Field(
    #     default=["--live", "--stream", "--comments", "tiktok", "youtube", "facebook"],
    #     description="List of keywords for the data collector"
    # )

    # defaults : Optional[List[Any]] = Field(
    #     default=["tiktok", "youtube", "facebook"],
    #     description="Default values for the data collector"
    # )

    # helps: Optional[List[str]] = Field(
    #     default=["Data collector for TikTok live comments", "Data collector for YouTube live comments", "Data collector for Facebook live comments"],
    #     description="Help messages for the data collector"
    # )
