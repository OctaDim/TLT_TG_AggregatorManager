from typing import Union, Type, List, Any, Tuple, Dict

from configs.console_colors import CONSOLE_COLORS
from configs.options import TELETHON_OPTIONS
from utils_common.exec_time_decorator import execution_time_decorator


@execution_time_decorator(
    in_seconds=False,
    note="get_attr_value_by_attr_chain",
    exec_time_logging=TELETHON_OPTIONS.LOG_EXEC_TIME_GET_EACH_ATTR,
    new_line_after=False)
async def get_attr_value_by_attr_chain(
        base_class_or_obj: Union[Type, object],
        attribute_chain: Union[str, List[str], Tuple[str], None]
) -> Any | None:
    if not base_class_or_obj:
        return None

    if isinstance(attribute_chain, (list, tuple)):
        all_attributes_list = attribute_chain
    elif isinstance(attribute_chain, str):
        all_attributes_list = attribute_chain.strip().split(".")
    else:
        all_attributes_list = None

    if not all_attributes_list:
        return base_class_or_obj

    cur_chained_obj_val = base_class_or_obj
    all_attributes_list = [attr_str.strip() for attr_str in all_attributes_list]  # Remove spaces
    for cur_attr in all_attributes_list:
        if not hasattr(cur_chained_obj_val, cur_attr):
            if TELETHON_OPTIONS.LOG_NON_EXISTING_ATTR_ERROR:
                blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
                yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
                reset_clr = CONSOLE_COLORS.RESET
                print(f"Non existing attribute skipped [ERROR]:\n"
                      f"cur_attr: {yellow_clr}{cur_attr}{reset_clr}\n"
                      f"all_attributes_chain: {blue_clr}{attribute_chain}{reset_clr}\n")
            return None
        cur_chained_obj_val = getattr(cur_chained_obj_val, cur_attr)
    return cur_chained_obj_val


async def get_attrs_values_by_attr_chains(
        base_class_or_obj: Union[Type, object],
        attributes_chains_dict: Dict[str, Dict[str, Union[str, List[str], Tuple[str], None]]],
        section_separator_prefix: str
) -> Dict[str, any]:
    if not base_class_or_obj or not attributes_chains_dict:
        return {}

    all_attrs_values_dict = {}
    sep_counter = 1
    for cur_attr_section, cur_attr_chains in attributes_chains_dict.items():
        for cur_attr_str, cur_attr_chain in cur_attr_chains.items():
            if cur_attr_str.startswith(section_separator_prefix):
                counted_attr_str = f"{cur_attr_str}_{sep_counter}"
                all_attrs_values_dict[counted_attr_str] = cur_attr_chain
                sep_counter += 1
                continue

            cur_attr_str = cur_attr_str.strip()
            cur_attr_chain = cur_attr_chain.strip()
            cur_attr_value = await get_attr_value_by_attr_chain(
                base_class_or_obj=base_class_or_obj,
                attribute_chain=cur_attr_chain)
            all_attrs_values_dict[cur_attr_str] = cur_attr_value
    return all_attrs_values_dict
