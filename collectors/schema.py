from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

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

    text: str = Field(
        ...,
        description="Text content of the comment",
        min_length=1
    )
    language: Optional[str] = Field(
        default=None,
        description="Language of the comment text"
    )
    ts_event_utc: datetime = Field(
        ...,
        description="Timestamp of the event in UTC",
        example="2023-10-01T12:00:00Z"
    )
