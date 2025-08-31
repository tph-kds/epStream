import os 
from config import CommentSchemaConfig
from typing import Optional

from TikTokLive import TikTokLiveClient

from TikTokLive.events import (
    ConnectEvent, 
    CommentEvent, 
    LikeEvent, 
    GiftEvent, 
    FollowEvent, 
    ShareEvent, 
    ViewerCountUpdateEvent
)

class TikTokData:
    def __init__(self, comment_config: CommentSchemaConfig):
        super(self.__class__, self).__init__()
        self.comment_config = comment_config
        self.__init_vars__()

        # Init client platform
        self.client: Optional[TikTokLiveClient] = self.init_client()

    def __init_vars__(self):
        print(f"Initializing TikTokData with config: {self.comment_config}")
        self.host_id = self.comment_config.host_id
        self.platform = self.comment_config.platform or "tiktok"
        self.events = self.comment_config.events or ["comment"]
        self.number_of_comments = self.comment_config.number_of_comments or 10
        print(f"Initialized with host_id: {self.host_id}, platform: {self.platform}, events: {self.events}, number_of_comments: {self.number_of_comments}")

    def init_tiktok_client(self) -> TikTokLiveClient:
        self.client: TikTokLiveClient = TikTokLiveClient(unique_id=self.host_id)
        return self.client

    def init_youtube_client(self):
        pass 

    def init_facebook_client(self):
        pass 

    def init_client(self) -> Optional[TikTokLiveClient]:
        if self.platform == "tiktok":
            self.client = self.init_tiktok_client()
        elif self.platform == "youtube":
            self.client = self.init_youtube_client()
        elif self.platform == "facebook":
            self.client = self.init_facebook_client()

        return self.client

    def run_tiktok_data_collection(self):
        print(f"Starting TikTok data collection for host: {self.host_id}")
        print(f"Platform: {self.platform}")
        print(f"Events: {self.events}")
        print(f"Number of comments to collect: {self.number_of_comments}")

    def stop_tiktok_data_collection(self):
        pass

    def get_data(self):
        pass 
