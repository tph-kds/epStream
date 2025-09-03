import os 
from typing import Optional, List, Dict 
from base_mpd import BaseData
from collectors.outer_models.config import CleanerModelingInput
from collectors.outer_models.model import CleanerModeling
from config import (
    CommentSchemaConfig, 
    MultiPlatformDataConfig,
    MultiPlatformDataOutput
)

from TikTokLive import TikTokLiveClient
from tiktok_data import TikTokData
from youtube_data import YouTubeData
from facebook_data import FacebookData

from collectors.outer_models import (
    CleanerModelingInput, 
    CleanerModelingOutput,
    TargetOutput,
    system_prompt
)



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

    def run_data_collection(self) -> MultiPlatformDataOutput:
        print(f"Starting data collection for host: {self.host_id}")
        print(f"Platform: {self.platform}")
        print(f"Events: {self.events}")
        print(f"Number of comments to collect: {self.number_of_comments}")
        print(f"Be ready for data collection!")

        original_comments_data = self.tiktok_platform.get_data()
        print(f"Successfully collected comments data")
        cleaned_comments_data = self.__cleaned_data(original_comments_data)
        print(f"Your system have cleaned data output successfully.")   
             
        return MultiPlatformDataOutput(**cleaned_comments_data)


    def stop_data_collection(self):
        if self.client:
            self.client.stop()
        print(f"Stopped data collection for host: {self.host_id}")

    def get_original_data(self):
        if self.platform == "tiktok":
            return self.tiktok_platform.get_data(self.client)
        elif self.platform == "youtube":
            return self.youtube_platform.get_data(self.client)
        elif self.platform == "facebook":
            return self.facebook_platform.get_data(self.client)
    

    def __cleaned_data(self, comments_data: MultiPlatformDataOutput) -> MultiPlatformDataOutput:
        # Call the outer model to clean the data
        output_cleaned = self.__call_outer_model(comments_data["comments"])
        
        # Hanlding the original dict output after calling 
        # # Insert all languages into the output
        for key, value in comments_data.items():
            if key == "langs":
                # Delete all data in langs
                comments_data[key] = []
                # Insert all languages into the output
                comments_data["langs"] = output_cleaned.cleaned_text["languages"]
        # Insert into comments_data with a new attribute: "comments"
        comments_data["comments"] = output_cleaned.cleaned_text["text"]

        return MultiPlatformDataOutput(**comments_data)


    def __call_outer_model(
            self, 
            cleaned_data: List[str],
            prompt_input_user: Optional[str]
    ) -> CleanerModelingOutput:
        prompt_input = prompt_input_user + "In addition, let's clean up the following data below: " + "[ " + ", ".join(cleaned_data) + " ]"
        cleaner_model_config = CleanerModelingInput(
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-001"),
            prompt_input=prompt_input,
            system_instruction=system_prompt,

        )

        cleaner_model = CleanerModeling(input_config=cleaner_model_config)
        response = cleaner_model.run()
        print("\n ================== \n Response from Gemini Model:")
        print(response)
        print("\n ================== \n")
        print(f"Cleaned Text: {response.cleaned_text}")
        print(f"\nMessages: {response.messages}")

        return response

