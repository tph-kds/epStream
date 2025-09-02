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
        self.client: Optional[TikTokLiveClient] = self._init_client()

    def __init_vars__(self):
        print(f"Initializing MultiPlatformData with config: {self.mpd_config}")
        self.platform = self.mpd_config.platform or ""
        self.tiktok_platform_config = self.mpd_config.tiktok_platform_config or ""
        self.youtube_platform_config = self.mpd_config.youtube_platform_config or ""
        self.facebook_platform_config = self.mpd_config.facebook_platform_config or ""

        if self.platform == "tiktok":
            self.tiktok_platform = TikTokData(self.tiktok_platform_config)
            print(f"Initialized TikTok platform with config: {self.tiktok_platform_config}")
        elif self.platform == "youtube":
            self.youtube_platform = YouTubeData(self.youtube_platform_config)
            print(f"Initialized YouTube platform with config: {self.youtube_platform_config}")
        elif self.platform == "facebook":
            self.facebook_platform = FacebookData(self.facebook_platform_config)
            print(f"Initialized Facebook platform with config: {self.facebook_platform_config}")

    def _init_client(self) -> Optional[TikTokLiveClient]:
        if self.platform == "tiktok":
            self.client = self.tiktok_platform.client
        elif self.platform == "youtube":
            self.client = self.youtube_platform.client
        elif self.platform == "facebook":
            self.client = self.facebook_platform.client

        print(f"Initialized client name is {self.client} for platform: {self.platform}")

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
            return self.tiktok_platform.get_data(self.client)
        elif self.platform == "youtube":
            return self.youtube_platform.get_data(self.client)
        elif self.platform == "facebook":
            return self.facebook_platform.get_data(self.client)
