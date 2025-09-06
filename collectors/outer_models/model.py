from google import genai
from google.genai import types

from collectors.outer_models.config import (
    CleanerModelingInput, 
    CleanerModelingOutput,
    TargetOutput
)

class CleanerModeling:
    def __init__(self, input_config: CleanerModelingInput):
        self.input_config = input_config
        self.gemini_api_key = self.input_config.gemini_api_key
        self.model_name = self.input_config.model_name if hasattr(self.input_config, 'model_name') else "gemini-2.0-flash-001"
        self.prompt_input = self.input_config.prompt_input
        self.system_instruction = self.input_config.system_instruction if hasattr(self.input_config, 'system_instruction') else "You are a helpful assistant that provides information about the Gemini API."
        self.temperature = self.input_config.temperature
        self.top_p = self.input_config.top_p
        self.top_k = self.input_config.top_k
        self.candidate_count = self.input_config.candidate_count
        self.seed = self.input_config.seed
        self.max_output_tokens = self.input_config.max_output_tokens
        self.stop_sequences = self.input_config.stop_sequences
        self.presence_penalty = self.input_config.presence_penalty
        self.frequency_penalty = self.input_config.frequency_penalty

        self.client = self.__init_client()

    def __init_client(self):
        client = genai.Client(
            api_key=self.gemini_api_key
        )
        if self.gemini_api_key:
            print("Gemini Client initialized.")
            print(f"Using model: {self.model_name}")
        else:
            print("Gemini Client not initialized.")

        return client

    def __contents(self):
        return types.Part.from_text(
            text=self.prompt_input
        )

    def __generate_content_config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            candidate_count=self.candidate_count,
            seed=self.seed,
            max_output_tokens=self.max_output_tokens,
            stop_sequences=self.stop_sequences or ["STOP!"],
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                )
            ],
            response_mime_type='application/json',
            response_schema=TargetOutput,
        )

    def run(self) -> CleanerModelingOutput:
        # Implement the cleaning logic here
        messages = "Cleaning process completed successfully."

        response = self.client.models.generate_content(
            model= self.model_name,
            contents = self.__contents(),
            config = self.__generate_content_config(),
        )

        print(f"Response from Gemini Model: {response}")

        if not response:
            messages = "Cleaning process failed."

        return CleanerModelingOutput(
            cleaned_text={
                "text": response.parsed.data if response and response.parsed else [],
                "languages": response.parsed.languages if response and response.parsed else [],
            },
            messages=messages
        )
