from configs.options import TELETHON_OPTIONS


async def log_all_event_params(
        log_title: str,
        event_params_dict: dict
) -> None:
    print(f"\n{log_title}"
          f"\n{'=' * 80}")
    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    for cur_param_str, cur_param_val in event_params_dict.items():
        if cur_param_str.startswith(separator):
            print(f"\t")
            continue
        if cur_param_val is None:
            print(f"\t{cur_param_str} ==")
        else:
            print(f"\t{cur_param_str} == {cur_param_val} ({type(cur_param_val)})")
    print(f"{'=' * 80}\n{'=' * 80}\n")
