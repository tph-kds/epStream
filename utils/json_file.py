import json
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class JsonFileConfig(BaseModel):
    source_path: str = Field(..., description="Path to the source file")
    file_name: Optional[str] = Field(..., description="Name of the file")

class JsonFile:
    def __init__(self, json_config: JsonFileConfig):
        super(JsonFile, self).__init__()
        self.json_config = json_config

        self.source_path = self.json_config.source_path
        self.file_name = self.json_config.file_name

        self.file_path = f"{self.source_path}/{self.file_name}"

    def save_json(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def load_json(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


if __name__ == "__main__":
    json_config = JsonFileConfig(source_path="./examples/logs", file_name="test.json")
    json_file = JsonFile(json_config=json_config)
    json_file.save_json({"comments_data": []})
    

