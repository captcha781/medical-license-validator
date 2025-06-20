import json
from pprint import pprint


def pydantic_to_form_error(json_data):
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    error = {}
    for item in json_data:
        loc = item.get("loc")
        msg = item.get("msg")
        type = item.get("type")

        for l in loc:
            error[l] = msg

    return error
