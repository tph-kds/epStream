from pydantic import BaseModel, Field
from typing import Optional

class CommentSchemaConfig(BaseModel):
    host_id: str = Field(..., description="Unique identifier for the host user who organized the stream (e.g., user123)")
    platform: str = Field(..., description="Platform where the comment is made (e.g., tiktok, youtube, facebook)")
    events: Optional[list[str]] = Field(
        ..., 
        description="List of events associated with the information to be collected (e.g., comment, like, share, gifted, ...)",
        default=["comment"]
    )
    number_of_comments: Optional[int] = Field(
        ..., 
        description="Number of comments to collect",
        default=10
    )

class CommentSchemaOutput(BaseModel):
    pass 


class MultiPlatformDataConfig(BaseModel):
    platform: str = Field(..., description="Platform for multi-platform data collection (e.g., tiktok, youtube, facebook)")

    tiktok_platform: CommentSchemaConfig = Field(..., description="TikTok platform configuration")
    youtube_platform: CommentSchemaConfig = Field(..., description="YouTube platform configuration")
    facebook_platform: CommentSchemaConfig = Field(..., description="Facebook platform configuration")


class MultiPlatformDataOutput(BaseModel):
    pass 