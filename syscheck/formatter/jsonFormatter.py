import json

def to_json(results: dict) -> None:
    print(json.dumps(results, indent=4))