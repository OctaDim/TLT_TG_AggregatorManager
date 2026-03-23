async def get_bool_none_from_str(
        orig_value: str | bool | None
) -> bool | None:
    if isinstance(orig_value, str):
        orig_value = orig_value.lower()

    if orig_value in ["true", ]:
        new_value = True
    elif orig_value in ["false", ]:
        new_value = False
    elif orig_value in ["none", "null"]:
        new_value = None
    else:
        new_value = orig_value
    return new_value
