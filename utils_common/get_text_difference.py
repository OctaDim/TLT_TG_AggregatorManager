import difflib
from typing import Dict, Union


async def get_text_difference_str(
        old_text: str,
        new_text: str
) -> Dict[str, Union[list, str]]:
    old_words = list(old_text)
    new_words = list(new_text)
    differences = difflib.SequenceMatcher(a=old_words, b=new_words,
                                          isjunk=None, autojunk=True)
    removed_parts = []
    added_parts = []
    all_changed_parts = []

    for opcode in differences.get_opcodes():
        if opcode[0] == "delete":
            cur_removed_part = "".join(old_words[opcode[1]:opcode[2]])
            cur_removed_str = f'"(X){cur_removed_part.strip()}"'
            removed_parts.append(cur_removed_part)
            all_changed_parts.append(cur_removed_str)
        elif opcode[0] == "insert":
            cur_inserted_part = "".join(new_words[opcode[3]:opcode[4]])
            cur_inserted_str = f'"(+){cur_inserted_part.strip()}"'
            added_parts.append(cur_inserted_part)
            all_changed_parts.append(cur_inserted_str)
        elif opcode[0] == "replace":
            cur_removed_part = "".join(old_words[opcode[1]:opcode[2]])
            removed_parts.append(cur_removed_part)

            cur_added_part = "".join(new_words[opcode[3]:opcode[4]])
            added_parts.append(cur_added_part)

            cur_replaced_str = f'"{cur_removed_part}"<=="{cur_added_part}"'
            all_changed_parts.append(cur_replaced_str)

    all_changes_str = "   ".join(all_changed_parts)
    differences_data = {
        "removed_parts": removed_parts,
        "added_parts": added_parts,
        "all_changed_parts": all_changed_parts,
        "all_changes_str": all_changes_str}
    return differences_data
