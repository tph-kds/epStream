from pydantic import BaseModel, Field
from typing import List, Optional

class CommentSchemaConfig(BaseModel):
    host_id: str = Field(..., description="Unique identifier for the host user who organized the stream (e.g., user123)")
    platform: str = Field(..., description="Platform where the comment is made (e.g., tiktok, youtube, facebook)")
    events: Optional[List[str]] = Field(
        ..., 
        description="List of events associated with the information to be collected (e.g., comment, like, share, gifted, ...)",
        # default=["comment"]
    )
    number_of_comments: Optional[int] = Field(
        ..., 
        description="Number of comments to collect",
        # default=10
    )
    client_name: Optional[str] = Field(
        ..., 
        description="Name of the client for the platform (e.g., tiktok_client, youtube_client, facebook_client)",
        # default="tiktok_client"
    )



class MultiPlatformDataConfig(BaseModel):
    platform: str = Field(..., description="Platform for multi-platform data collection (e.g., tiktok, youtube, facebook)")

    tiktok_platform_config: Optional[CommentSchemaConfig] = Field(
        default=None, 
        description="TikTok platform configuration"
    )
    youtube_platform_config: Optional[CommentSchemaConfig] = Field(
        default=None, 
        description="YouTube platform configuration"
    )
    facebook_platform_config: Optional[CommentSchemaConfig] = Field(
        default=None, 
        description="Facebook platform configuration"
    )


class MultiPlatformDataOutput(BaseModel):
    comment_ids: List[str] = Field(..., description="Unique identifier for the comment(e.g., 1_uuid4, 2_sdsd)")
    platforms: List[str] = Field(..., description="Platform for the comment (e.g., tiktok, youtube, facebook)")
    stream_ids: List[str] = Field(..., description="Unique identifier for the stream")
    user_ids: List[str] = Field(..., description="Unique identifier for the user")
    usernames: List[str] = Field(..., description="Username of the user")
    texts: Optional[List[str]] = Field(default=None, description="The original text content of the comment")
    comments: Optional[List[str]] = Field(default=None, description="List of comments after cleaning structure comment")
    langs: List[str] = Field(..., description="Language of the comment")
    ts_event_utc_mss: List[int] = Field(..., description="Timestamp of the event in UTC milliseconds (e.g., 1633072800000)")
    ts_events: List[str] = Field(..., description="Timestamp of the event in ISO format (e.g., 2021-10-01T00:00:00Z)")

# class MultiPlatformDataOutput(BaseModel):
#     comment_id: List[str] = Field(..., description="Unique identifier for the comment(e.g., 1_uuid4, 2_sdsd)")
#     platform: List[str] = Field(..., description="Platform for the comment (e.g., tiktok, youtube, facebook)")
#     stream_id: List[str] = Field(..., description="Unique identifier for the stream")
#     user_id: List[str] = Field(..., description="Unique identifier for the user")
#     username: List[str] = Field(..., description="Username of the user")
#     text: List[str] = Field(..., description="The original text content of the comment")
#     comments: Optional[List[str]] = Field(..., description="List of comments after cleaning structure comment")
#     lang: List[str] = Field(..., description="Language of the comment")
#     ts_event_utc_ms: List[int] = Field(..., description="Timestamp of the event in UTC milliseconds (e.g., 1633072800000)")
#     ts_event: List[str] = Field(..., description="Timestamp of the event in ISO format (e.g., 2021-10-01T00:00:00Z)")

class CommentSchemaConfigOutput(MultiPlatformDataOutput):
    pass
