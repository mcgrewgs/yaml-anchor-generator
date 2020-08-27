from typing import Dict, Union, List, Any, Tuple, Optional
import re

INDENT_INC = 2

YAMLValue = Union[int, bool, str, "YAMLMap", "YAMLList", List[Any], Dict[str, Any]]


def val_to_label_key(v: YAMLValue) -> str:
    return str(type(v)) + " " + str(v)


class YAMLMap:
    indent: int
    labels: Dict[str, Tuple[str, int]]
    key_vals: Dict[str, YAMLValue]

    def __init__(
        self: "YAMLMap",
        indent_num: int = 0,
        l: Dict[str, Tuple[str, int]] = {},
        kv: Dict[str, YAMLValue] = {},
    ):
        self.indent = indent_num
        self.key_vals = kv
        self.labels = l

    def yaml_map_to_string(self: "YAMLMap") -> str:
        str_builder = "\n"
        for k, v in self.key_vals.items():
            lk = val_to_label_key(v)
            print(f"{v}: {lk}")
            if lk in self.labels:
                self.labels[lk] = (self.labels[lk][0], self.labels[lk][1] + 1)
                str_builder += (" " * self.indent) + f"{k}: *{self.labels[lk][0]}\n"
            else:
                self.labels[lk] = (f"label{len(self.labels)}", 0)
                str_builder += (
                    (" " * self.indent)
                    + f"{k}: &{self.labels[lk][0]} {parent_to_string(v, self.labels, self.indent + INDENT_INC).rstrip()}\n"
                )

        return str_builder


class YAMLList:
    indent: int
    labels: Dict[str, Tuple[str, int]]
    vals: List[YAMLValue]

    def __init__(
        self: "YAMLList",
        indent_num: int = 0,
        l: Dict[str, Tuple[str, int]] = {},
        v: List[YAMLValue] = [],
    ):
        self.indent = indent_num
        self.vals = v
        self.labels = l

    def yaml_list_to_string(self: "YAMLList") -> str:
        str_builder = "\n"
        for v in self.vals:
            lk = val_to_label_key(v)
            print(f"{v}: {lk}")
            if lk in self.labels:
                self.labels[lk] = (self.labels[lk][0], self.labels[lk][1] + 1)
                str_builder += (" " * self.indent) + f"- *{self.labels[lk][0]}\n"
            else:
                self.labels[lk] = (f"label{len(self.labels)}", 0)
                str_builder += (
                    (" " * self.indent)
                    + f"- &{self.labels[lk][0]} {parent_to_string(v, self.labels, self.indent + INDENT_INC).rstrip()}\n"
                )

        return str_builder


sample = YAMLMap(0, {}, {"a": "b", "c": 2, "d": 2, "e": "b", "f": 0, "g": [2]})


def parent_to_string(
    input: YAMLValue, l: Dict[str, Tuple[str, int]] = {}, indent: int = 0
) -> str:
    if isinstance(input, str):
        return f'"{input}"'
    elif isinstance(input, int) or isinstance(input, bool):
        return f"{input}"
    elif isinstance(input, List):
        return parent_to_string(YAMLList(indent, l, input), l, indent)
    elif isinstance(input, Dict):
        return parent_to_string(YAMLMap(indent, l, input), l, indent)
    elif isinstance(input, YAMLMap):
        return input.yaml_map_to_string()
    elif isinstance(input, YAMLList):
        return input.yaml_list_to_string()
    else:
        return ""


def scrub_unused_labels(str_builder: str, l: Dict[str, Tuple[str, int]]) -> str:
    for _, v in l.items():
        if v[1] == 0:
            str_builder = str_builder.replace(f"&{v[0]} ", "")
    str_builder = re.sub("-\\s*\n\\s*", "- ", str_builder)
    return str_builder


def dumps(input: YAMLValue) -> str:
    l = {}
    s = parent_to_string(input, l, 0)
    return scrub_unused_labels(s, l)
