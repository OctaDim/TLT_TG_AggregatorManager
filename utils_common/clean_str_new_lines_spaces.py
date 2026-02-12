import re


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
