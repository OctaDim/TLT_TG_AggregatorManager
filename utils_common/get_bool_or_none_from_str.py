async def get_bool_none_from_str(
        orig_value: str | bool | None
) -> bool | None:
    if isinstance(orig_value, str):
        orig_value = orig_value.lower()

    if orig_value in ["true", ]:
        result_value = True
    elif orig_value in ["false", ]:
        result_value = False
    elif orig_value in ["none", "null"]:
        result_value = None
    else:
        result_value = orig_value
    return result_value
