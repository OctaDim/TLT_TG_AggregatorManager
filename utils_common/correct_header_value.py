def correct_header_str_value(orig_str: str) -> str:
    """Convert any string to Latin-1 compatible (headers suitable) string"""
    if orig_str is None:
        return ""
    value_str = str(orig_str)
    try:
        value_str.encode("latin-1")
        return value_str
    except UnicodeEncodeError:
        # Replacing non Latin-1 characters with their escaped representation
        escaped_str = value_str.encode('unicode-escape').decode('ascii')
        return escaped_str
