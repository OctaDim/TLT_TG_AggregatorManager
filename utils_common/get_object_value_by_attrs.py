from typing import Union, Type, List, Any, Tuple

from utils_common.exec_time_decorator import execution_time_decorator


@execution_time_decorator(in_seconds=False,
                          note="get_obj_value_by_attrs_chain",
                          exec_time_logging=True,
                          new_line_after=False)
def get_obj_value_by_attrs_chain(
        base_class_or_obj: Union[Type, object],
        all_attributes_chain: Union[str, List[str], Tuple[str], None]
) -> Any | None:
    if not base_class_or_obj:
        return None

    if isinstance(all_attributes_chain, (list, tuple)):
        all_attributes_list = all_attributes_chain
    elif isinstance(all_attributes_chain, str):
        all_attributes_list = all_attributes_chain.strip().split(".")
    else:
        all_attributes_list = None

    if not all_attributes_list:
        return base_class_or_obj

    cur_chained_obj_val = base_class_or_obj
    for cur_attr in all_attributes_list:
        if not hasattr(cur_chained_obj_val, cur_attr):
            print("Non existing attribute, parameter skipped [ERROR]")
            return None
        cur_chained_obj_val = getattr(cur_chained_obj_val, cur_attr)
    return cur_chained_obj_val
