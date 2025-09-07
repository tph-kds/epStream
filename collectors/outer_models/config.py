from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional, List, Dict 

class CleanerModelingInput(BaseModel):
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    model_name: str = Field(..., description="Name of the Gemini model to use (E.g. 'gemini-2.0-flash-001')")
    prompt_input: str = Field(..., description="Input text to be processed by the model (e.g. 'Please clean this text.')")
    system_instruction: str = Field(..., description="System instruction for the model")
    # Add other fields as needed
    temperature: Optional[float] = Field(0, description="Sampling temperature")
    top_p: Optional[float] = Field(0.95, description="Top-p sampling")
    top_k: Optional[int] = Field(20, description="Top-k sampling")
    candidate_count: Optional[int] = Field(1, description="Number of response candidates to generate")
    seed: Optional[int] = Field(5, description="Random seed for reproducibility")
    max_output_tokens: Optional[int] = Field(1024, description="Maximum number of tokens in the output")
    stop_sequences: Optional[List[str]] = Field(default_factory=list, description="List of stop sequences")
    presence_penalty: Optional[float] = Field(0.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(0.0, description="Frequency penalty")

class CleanerModelingOutput(BaseModel):
    cleaned_text: Dict[str, List[str]] = Field(
        ..., 
        description="Dictionary with cleaned text segments",
    )
    messages: str = Field(..., description="Detailed messages about the cleaning process")

class TargetOutput(BaseModel):
    languages: List[str] = Field(..., description="Language of the text (Eg. 'en', 'fr', 'es')")
    data: List[str] = Field(..., description="List of responses")