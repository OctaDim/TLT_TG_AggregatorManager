import json

from datetime import datetime
from typing import Tuple


async def get_jsonable_value(
        orig_object: any,
        object_log_name: str = None,
        log_invalid_json: bool = False
) -> Tuple[str, any] | None:
    try:
        if isinstance(orig_object, datetime):
            jsonable_obj = orig_object.isoformat()
        else:
            jsonable_obj = orig_object
        json.dumps(jsonable_obj)
        return "jsonable", jsonable_obj
    except Exception as error:
        if log_invalid_json:
            print(f"JSON serialization [ERROR]: error: {error}\n"
                  f"object_name: {object_log_name}\n"
                  f"object_value: {orig_object}\n")
        return None
