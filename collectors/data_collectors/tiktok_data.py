import os, json, time, uuid

import asyncio
from datetime import datetime, timezone 
from config import CommentSchemaConfig, CommentSchemaConfigOutput
from typing import Optional, Dict, List, Any

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
        self.client: Optional[TikTokLiveClient] = self._init_tiktok_client()["client"]
        self.client_name: Optional[str] = self._init_tiktok_client()["client_name"]

        self.__data_count: Optional[int] = 0

    def __init_vars__(self):
        print(f"Initializing TikTokData with config: {self.comment_config}")
        self.host_id = self.comment_config.host_id
        self.platform = self.comment_config.platform or "tiktok"
        self.events = self.comment_config.events or ["comment"]
        self.number_of_comments = self.comment_config.number_of_comments or 10
        print(f"Initialized with host_id: {self.host_id}, platform: {self.platform}, events: {self.events}, number_of_comments: {self.number_of_comments}")

        # Internal Vars
        self.__stream_id: str = ""
        self.__host_id: str = ""


        self.__comments: List[str] = []
        self.__usernames: List[str] = []
        self.__ts_events: List[str] = []
        self.__ts_event_utc_mss: List[int] = []
        self.__langs: List[str] = []
        self.__comment_ids: List[str] = []
        self.__stream_ids: List[str] = []
        self.__user_ids: List[str] = []
        self.__platforms: List[str] = []

        self.__data_list: Dict[str, List[Any]] = {
            "stream_ids": self.__stream_ids,
            "platforms": self.__platforms,
            "comment_ids": self.__comment_ids,
            "usernames": self.__usernames,
            "user_ids": self.__user_ids,
            "comments": self.__comments,
            "langs": self.__langs,
            "ts_events": self.__ts_events,
            "ts_event_utc_mss": self.__ts_event_utc_mss
        }

    def _init_tiktok_client(self) -> Dict[str, Optional[object | TikTokLiveClient]]:
        self.client: TikTokLiveClient = TikTokLiveClient(unique_id=self.host_id)
        return {
            "client": self.client,
            "client_name": self.comment_config.client_name or "tiktok_client"    
        }

    def run_tiktok_data_collection(self):
        print(f"Starting TikTok data collection for host: {self.host_id}")
        print(f"Platform: {self.platform}")
        print(f"Events: {self.events}")
        print(f"Number of comments to collect: {self.number_of_comments}")

        if self.client:
            self.client.run()
        else:
            print("Failed to initialize TikTok client.")

    def stop_tiktok_data_collection(self):
        pass

    def get_data(self) -> Dict[str, List[Any]]:
        print(f"Getting data for host: {self.host_id}")
        # Access Tiktok API to get the data
        self.client.add_listener(CommentEvent, self.__on_comment)

        # Run the client TikTok to get the data
        asyncio.run(self.client.connect())

        print(f"Collected {self.__data_count} comments for host: {self.host_id} successfully.")
        print(f"Total data collected: {len(self.__data_list)}")

        return self.__data_list


    # def get_one_data(self) -> CommentSchemaConfigOutput:
    #     print(f"The {self.__data_count} time is getting the data for host: {self.host_id}")
    #     # Access Tiktok API to get the data
    #     self.client.add_listener(CommentEvent, self.__on_comment)
    #     # self.client.add_listener(GiftEvent, self.__on_gift)
    #     # self.client.add_listener(LikeEvent, self.__on_like)
    #     # self.client.add_listener(FollowEvent, self.__on_follow)
    #     # self.client.add_listener(ShareEvent, self.__on_share)
    #     # self.client.add_listener(ViewerCountUpdateEvent, self.__on_viewer_count_update)

    #     # Run the client TikTok to get the data
    #     asyncio.run(self.client.connect())

    #     # Generate the initial extracted data
    #     comment_id: str = self.__data_count + str(uuid.uuid4())
    #     stream_id: str = "stream-001"
    #     user_id: str = "utest-" + str(uuid.uuid4())[:8]
    #     username: str = "user_test__" + str(uuid.uuid4())[:5]
    #     comment: str = "This is a test comment"
    #     lang: str = "en"
    #     ts_event_utc_ms: int = int(datetime.now(timezone.utc).timestamp() * 1000)
    #     ts_event: str = datetime.now(timezone.utc).isoformat()

    #     return CommentSchemaConfigOutput(
    #         comment_id = comment_id,
    #         platform = self.platform,
    #         stream_id = stream_id,
    #         user_id = user_id,
    #         username = username,
    #         text = comment,
    #         lang = lang,
    #         ts_event_utc_ms = ts_event_utc_ms,
    #         ts_event = ts_event
    #     )

    async def on_connect(self, event: ConnectEvent):
        print(f"Connected to @{event.unique_id} (Room ID: {self.client.room_id}")
        if self.__host_id == "" or self.__stream_id == "":
            self.__host_id = self.client.room_id
            self.__stream_id = event.unique_id


    # Or, add it manually via "client.add_listener()"
    async def on_comment(self, event: CommentEvent) -> Dict[str, Any]:
        # print(f"{event.user.nickname} -> {event.comment}")
        comment = event.comment
        if len(comment) > 10:
            self.__data_count += 1
            self.__platforms.append(self.platform)
            self.__stream_ids.append(self.__stream_id)
            self.__usernames.append(event.user.nickname)
            self.__user_ids.append(event.user.display_id)
            self.__comment_ids.append(self.__data_count + str(uuid.uuid4()))
            self.__comments.append(comment)
            self.__langs.append("en")  # Placeholder for language detection 
            self.__ts_events.append(datetime.now(timezone.utc).isoformat())
            self.__ts_event_utc_mss.append(int(datetime.now(timezone.utc).timestamp() * 1000))

            print(f'TESTING {self.__usernames[-1]} - {comment} - {self.__data_count} - {self.__ts_event_utc_mss[-1]} - {self.__ts_events[-1]}')
            print("=======================================")
            self.__comments.append(comment)
            self.__usernames.append(event.user.nickname)

        if self.__data_count >= self.comment_config.number_of_comments - 1:
            await self.client.disconnect()
            await asyncio.sleep(2)

            # Get only data from the first comment to MAX_COMMENTS
            for i, key in enumerate(self.__data_list.keys()):
                print("Running here....")
                print(f"i is {i}, key is {key}")
                print(f"{self.__comments[:self.comment_config.number_of_comments]} - {self.__usernames[:self.comment_config.number_of_comments]} - {self.__ts_events[:self.comment_config.number_of_comments]} - {self.__ts_event_utc_mss[:self.comment_config.number_of_comments]}")
                if key == "platforms":
                    self.__data_list[key] = self.__platforms[:self.comment_config.number_of_comments]
                elif key == "comment_ids":
                    self.__data_list[key] = self.__comment_ids[:self.comment_config.number_of_comments]
                elif key == "comments":
                    self.__data_list[key] = self.__comments[:self.comment_config.number_of_comments]
                elif key == "stream_ids":
                    self.__data_list[key] = self.__stream_ids[:self.comment_config.number_of_comments]
                elif key == "user_ids":
                    self.__data_list[key] = self.__user_ids[:self.comment_config.number_of_comments]
                elif key == "usernames":
                    self.__data_list[key] = self.__usernames[:self.comment_config.number_of_comments]
                elif key == "langs":
                    self.__data_list[key] = self.__langs[:self.comment_config.number_of_comments]
                elif key == "ts_events":
                    self.__data_list[key] = self.__ts_events[:self.comment_config.number_of_comments]
                elif key == "ts_event_utc_mss":
                    self.__data_list[key] = self.__ts_event_utc_mss[:self.comment_config.number_of_comments]

            print(f"Stopped client after {self.comment_config.number_of_comments} iterations")

            return self.__data_list
