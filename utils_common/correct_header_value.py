from typing import Dict


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


def correct_header_strings(headers_params: dict) -> Dict[str, any]:
    """Convert header strings to Latin-1 compatible (headers suitable) string"""
    corrected_strings = {}
    for cur_param_name, cur_param_val in headers_params:
        if isinstance(cur_param_val, str):
            if cur_param_val is None:
                corrected_strings[cur_param_name] = ""
            value_str = str(cur_param_val)
            try:
                value_str.encode("latin-1")
                corrected_strings[cur_param_name] = value_str
            except UnicodeEncodeError:
                # Replacing non Latin-1 characters with their escaped representation
                escaped_str = value_str.encode('unicode-escape').decode('ascii')
                corrected_strings[cur_param_name] = escaped_str
    return corrected_strings
