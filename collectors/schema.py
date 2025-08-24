from pydantic import BaseModel, Field
from datetime import datetime


class CommentSchema(BaseModel):
    comment_id: str = Field(..., description="Unique identifier for the comment")
    platform: str = Field(..., description="Platform where the comment was made (e.g., TikTok)")
    stream_id: str = Field(..., description="Unique identifier for the stream")
    user_id: str | None = Field(
        ..., 
        description="Unique identifier for the user who made the comment",
        default=None
    )
    username: str | None = Field(
        ..., 
        description="Username of the user who made the comment",
        default=None
    )
    text: str = Field(
        ..., 
        description="Text content of the comment", 
        min_length=1
    )
    language: str | None = Field(
        ..., 
        description="Language of the comment text",
        default=None
    )
    ts_event_utc: datetime = Field(
        ..., 
        description="Timestamp of the event in UTC",
        example="2023-10-01T12:00:00Z"
    )
