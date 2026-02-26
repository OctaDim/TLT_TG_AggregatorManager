import re
from typing import Dict


async def group_clean_text(
        origin_texts: Dict[str, str],
        strip_spaces: bool = True,
        clean_line_breaks: bool = True,
        clean_continuous_spaces: bool = False,
) -> Dict[str, str]:
    if not origin_texts:
        return {}

    result_texts = {}
    for cur_name, cur_text in origin_texts.items():
        if strip_spaces:
            cur_text = cur_text.strip()
        if clean_continuous_spaces:
            cur_text = re.sub(pattern=r" {2,}", repl=" ",
                              string=cur_text)
        if clean_line_breaks:
            cur_text = re.sub(pattern=r"[\n\r]+", repl="  ",
                              string=cur_text)
        result_texts[cur_name] = cur_text
    return result_texts


async def clean_text(
        origin_text: str,
        strip_spaces: bool = True,
        clean_line_breaks: bool = True,
        clean_continuous_spaces: bool = False,
) -> str:
    if not origin_text:
        return ""

    result_text = None
    if strip_spaces:
        result_text = origin_text.strip()
    if clean_continuous_spaces:
        result_text = re.sub(pattern=r" {2,}", repl=" ",
                             string=result_text)
    if clean_line_breaks:
        result_text = re.sub(pattern=r"[\n\r]+", repl="  ",
                             string=result_text)
    return result_text
