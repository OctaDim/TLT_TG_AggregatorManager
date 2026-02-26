import json

from datetime import datetime
from typing import Tuple, Any, Dict, Union


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


async def get_only_jsonable_values(
        all_values: Dict[str, Any],
        separator: str = None
) -> Dict[str, Union[str, int, float, list, dict]]:
    jsonable_values = {}
    for cur_param_name, cur_param_value in all_values.items():
        jsonable_result = await get_jsonable_value(
            orig_object=cur_param_value,
            object_log_name=cur_param_name,
            log_invalid_json=True)

        if not jsonable_result or cur_param_name.startswith(separator):
            continue

        jsonable_values[cur_param_name] = jsonable_result[1]
    return jsonable_values
