import json

def validate_label(text):

    with open("rules/rule96.json", "r") as file:
        rules = json.load(file)

    results = {}

    lower = text.lower()

    for field in rules["mandatory_fields"]:

        found = False

        for keyword in field["keywords"]:

            if keyword.lower() in lower:
                found = True
                break

        results[field["name"]] = found

    return results