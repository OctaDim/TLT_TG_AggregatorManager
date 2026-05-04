def get_int_or_none_from_str(orig_string: str) -> int | None:
    try:
        return int(orig_string) if orig_string not in ["", None] else None
    except (ValueError, Exception) as error:
        print(f"Converting string to integer [ERROR]:\n"
              f"error: {error}\n"
              f"orig_string: {orig_string}\n")
        return None
