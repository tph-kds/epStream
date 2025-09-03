import os 
from collectors.outer_models.model import CleanerModeling
from collectors.outer_models.config import (
    CleanerModelingInput
)
from collectors.outer_models.prompt_setup import system_prompt

from dotenv import load_dotenv

load_dotenv()

def mock_data():
    return [
        "Cậu chơi game thật hay, mình muốn chơi cùng với cậu",
        "6368 Mãi yêu, mãi yêu",
        "Mày là con chó, bớt chơi lại mấy game này nhé",
        "Do you invite me into a room for starting a new match game?"
    ]
def main():
    prompt_input = "Let's clean up the following data below: " + "[ " + ", ".join(mock_data()) + " ]"
    cleaner_model_config = CleanerModelingInput(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        model_name="gemini-2.0-flash-001",
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

if __name__ == "__main__":
    main()
