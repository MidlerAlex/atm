import json

def create_json(file_name: str, data: dict[str, float]) -> None:
    with open(file_name, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


