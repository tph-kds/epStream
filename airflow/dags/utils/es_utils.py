import json, os, requests

def ensure_es_index_exists(es_url: str, index: str, mapping_path: str) -> None:
    # Check index
    r = requests.head(f"{es_url.rstrip('/')}/{index}")
    if r.status_code == 200:
        return
    # Create
    with open(mapping_path, "r", encoding="utf-8") as f:
        body = json.load(f)
    r = requests.put(f"{es_url.rstrip('/')}/{index}", json=body)
    r.raise_for_status()
