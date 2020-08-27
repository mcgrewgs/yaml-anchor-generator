from typing import Any, Dict, List, Tuple, Union
from yaml import full_load as parse
import re

INDENT_INC = 2

YAMLValue = Union[int, bool, str, List[Any], Dict[str, Any]]


def val_to_label_key(v: YAMLValue) -> str:
    return str(type(v)) + " " + str(v)


def label_name(i: int) -> str:
    return f"label{i:04}"


def yaml_map_to_string(
    key_vals: Dict[str, YAMLValue], labels: Dict[str, Tuple[str, int]], indent: int
) -> str:
    str_builder = "\n"
    for k, v in key_vals.items():
        lk = val_to_label_key(v)
        if lk in labels:
            labels[lk] = (labels[lk][0], labels[lk][1] + 1)
            str_builder += (" " * indent) + f"{k}: *{labels[lk][0]}\n"
        else:
            labels[lk] = (label_name(len(labels)), 0)
            str_builder += (
                (" " * indent)
                + f"{k}: &{labels[lk][0]} {parent_to_string(v, labels, indent + INDENT_INC).rstrip()}\n"
            )

    return str_builder


def yaml_list_to_string(
    vals: List[YAMLValue], labels: Dict[str, Tuple[str, int]], indent: int
) -> str:
    str_builder = "\n"
    for v in vals:
        lk = val_to_label_key(v)
        if lk in labels:
            labels[lk] = (labels[lk][0], labels[lk][1] + 1)
            str_builder += (" " * indent) + f"- *{labels[lk][0]}\n"
        else:
            labels[lk] = (label_name(len(labels)), 0)
            str_builder += (
                (" " * indent)
                + f"- &{labels[lk][0]} {parent_to_string(v, labels, indent + INDENT_INC).rstrip()}\n"
            )

    return str_builder


def parent_to_string(
    input: YAMLValue, l: Dict[str, Tuple[str, int]] = {}, indent: int = 0
) -> str:
    if isinstance(input, str):
        if "\n" in input:
            return "| \n" + " " * indent + input.replace("\n", "\n" + " " * indent)
        else:
            return f'"{input}"'
    elif isinstance(input, int) or isinstance(input, bool):
        return f"{input}"
    elif isinstance(input, List):
        return yaml_list_to_string(input, l, indent)
    elif isinstance(input, Dict):
        return yaml_map_to_string(input, l, indent)
    else:
        return ""


def scrub_unused_labels(str_builder: str, l: Dict[str, Tuple[str, int]]) -> str:
    i = 0
    for _, v in l.items():
        if v[1] == 0:
            str_builder = str_builder.replace(f"&{v[0]} ", "")
        else:
            str_builder = str_builder.replace(f"&{v[0]}", f"&{label_name(i)}")
            str_builder = str_builder.replace(f"*{v[0]}", f"*{label_name(i)}")
            i += 1
    str_builder = re.sub("-\\s*\n\\s*", "- ", str_builder)
    str_builder = re.sub(" +\\n", "\\n", str_builder)
    return str_builder


def dumps(input: YAMLValue) -> str:
    l = {}
    s = parent_to_string(input, l, 0)
    return scrub_unused_labels(s, l)
