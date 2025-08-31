import os 
from typing import Optional
from base_mpd import BaseData
from config import CommentSchemaConfig, MultiPlatformDataConfig

from TikTokLive import TikTokLiveClient
from tiktok_data import TikTokData
from youtube_data import YouTubeData
from facebook_data import FacebookData


class MultiPlatformData(BaseData):
    def __init__(self, mpd_config: MultiPlatformDataConfig):
        super(self.__class__, self).__init__()
        self.mpd_config = mpd_config
        self.__init_vars__()

        # Init client platform
        self.client: Optional[TikTokLiveClient] = self.init_client()

    def __init_vars__(self):
        print(f"Initializing MultiPlatformData with config: {self.mpd_config}")
        self.platform = self.mpd_config.platform or ""
        self.tiktok_platform = self.mpd_config.tiktok_platform or ""
        self.youtube_platform = self.mpd_config.youtube_platform or ""
        self.facebook_platform = self.mpd_config.facebook_platform or ""
        print(f"Initialized with tiktok_platform: {self.tiktok_platform}, youtube_platform: {self.youtube_platform}, facebook_platform: {self.facebook_platform}")

    def init_client(self) -> Optional[TikTokLiveClient]:
        if self.platform == "tiktok":
            self.client = self.init_tiktok_client()
        elif self.platform == "youtube":
            self.client = self.init_youtube_client()
        elif self.platform == "facebook":
            self.client = self.init_facebook_client()

        return self.client

    def run_data_collection(self):
        print(f"Starting data collection for host: {self.host_id}")
        print(f"Platform: {self.platform}")
        print(f"Events: {self.events}")
        print(f"Number of comments to collect: {self.number_of_comments}")

    def stop_data_collection(self):
        if self.client:
            self.client.stop()
        print(f"Stopped data collection for host: {self.host_id}")

    def get_data(self):
        if self.platform == "tiktok":
            return TikTokData.get_data(self.client)
        elif self.platform == "youtube":
            return YouTubeData.get_data(self.client)
        elif self.platform == "facebook":
            return FacebookData.get_data(self.client)
