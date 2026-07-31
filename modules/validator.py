import json

def validate_label(text):

    try:
        with open("rules/rule96.json", "r", encoding="utf-8") as file:
            rules = json.load(file)

    except Exception as e:
        return {"Rule File Error": str(e)}

    results = {}

    lower = text.lower()

    for field in rules["mandatory_fields"]:

        found = any(
            keyword.lower() in lower
            for keyword in field["keywords"]
        )

        results[field["name"]] = found

    return results