from typing import Any, Dict, List, Tuple, Union
from yaml import full_load as parse
import re
import sys

INDENT_INC = 2

YAMLValue = Union[int, bool, str, List[Any], Dict[str, Any]]


def label_name(partial_key: str) -> str:
    return f"label{partial_key}"


def dict_contains(parent: Dict[Any, Any], child: Dict[Any, Any]) -> bool:
    for k in child:
        if k not in parent:
            return False

    return True


def same_type(a: Any, b: Any) -> bool:
    return type(a) == type(b)


def count_overlap(parent: Dict[Any, Any], child: Dict[Any, Any]) -> int:
    overlap = 0
    for k in child:
        if same_type(parent[k], child[k]) and parent[k] == child[k]:
            overlap += 1

    return overlap


def yaml_map_to_string(
    key_vals: Dict[str, YAMLValue],
    labels: List[Tuple[YAMLValue, str, int]],
    indent: int,
    partial_key: str,
) -> str:
    if len(key_vals) == 0:
        return "{}"
    str_builder = "\n"
    for k, v in key_vals.items():
        is_labeled = False
        if isinstance(v, Dict):
            max_overlap = 0
            best_label_index = -1
            for i in range(len(labels)):
                if isinstance(labels[i][0], Dict) and dict_contains(v, labels[i][0]):
                    c = count_overlap(v, labels[i][0])
                    if c > max_overlap:
                        max_overlap = c
                        best_label_index = i
                        is_labeled = True
            if is_labeled:
                labels[best_label_index] = (
                    labels[best_label_index][0],
                    labels[best_label_index][1],
                    labels[best_label_index][2] + 1,
                )
                if max_overlap == len(v):
                    str_builder += (
                        " " * indent
                    ) + f"{k}: *{labels[best_label_index][1]}\n"
                else:
                    str_builder += (
                        (" " * indent)
                        + f"{k}: \n"
                        + (" " * (indent + INDENT_INC))
                        + f"<<: *{labels[best_label_index][1]}"
                    )
                    new_kv = {}
                    for kk, vv in v.items():
                        if (
                            kk not in labels[best_label_index][0]
                            or labels[best_label_index][0][kk] != vv
                        ):
                            new_kv[kk] = vv
                    str_builder += yaml_map_to_string(
                        new_kv, labels, indent + INDENT_INC, partial_key + "_" + k
                    )
        else:
            for i in range(len(labels)):
                if same_type(labels[i][0], v) and labels[i][0] == v:
                    is_labeled = True
                    labels[i] = (labels[i][0], labels[i][1], labels[i][2] + 1)
                    str_builder += (" " * indent) + f"{k}: *{labels[i][1]}\n"
                    break

        if not is_labeled:
            labels.append((v, label_name(partial_key + "_" + k), 0))
            str_builder += (
                (" " * indent)
                + f"{k}: &{labels[len(labels) - 1][1]} {parent_to_string(v, labels, indent + INDENT_INC, partial_key + '_' + k).rstrip()}\n"
            )

    return str_builder


def yaml_list_to_string(
    vals: List[YAMLValue],
    labels: List[Tuple[YAMLValue, str, int]],
    indent: int,
    partial_key: str,
) -> str:
    if len(vals) == 0:
        return "[]"
    str_builder = "\n"
    k = 0
    for v in vals:
        is_labeled = False
        is_labeled = False
        if isinstance(v, Dict):
            max_overlap = 0
            best_label_index = -1
            for i in range(len(labels)):
                if isinstance(labels[i][0], Dict) and dict_contains(v, labels[i][0]):
                    c = count_overlap(v, labels[i][0])
                    if c > max_overlap:
                        max_overlap = c
                        best_label_index = i
                        is_labeled = True
            if is_labeled:
                labels[best_label_index] = (
                    labels[best_label_index][0],
                    labels[best_label_index][1],
                    labels[best_label_index][2] + 1,
                )
                if max_overlap == len(v):
                    str_builder += (
                        " " * indent
                    ) + f"- *{labels[best_label_index][1]}\n"
                else:
                    str_builder += (
                        " " * indent
                    ) + f"- <<: *{labels[best_label_index][1]}"
                    new_kv = {}
                    for kk, vv in v.items():
                        if (
                            kk not in labels[best_label_index][0]
                            or labels[best_label_index][0][kk] != vv
                        ):
                            new_kv[kk] = vv
                    str_builder += yaml_map_to_string(
                        new_kv, labels, indent + INDENT_INC, partial_key + "_" + str(k)
                    )
        else:
            for i in range(len(labels)):
                if same_type(labels[i][0], v) and labels[i][0] == v:
                    labels[i] = (labels[i][0], labels[i][1], labels[i][2] + 1)
                    str_builder += (" " * indent) + f"- *{labels[i][1]}\n"
                    is_labeled = True
                    break
        if not is_labeled:
            labels.append((v, label_name(partial_key + "_" + str(k)), 0))
            str_builder += (
                (" " * indent)
                + f"- &{labels[len(labels) - 1][1]} {parent_to_string(v, labels, indent + INDENT_INC, partial_key + '_' + str(k)).rstrip()}\n"
            )
        k += 1

    return str_builder


def parent_to_string(
    input: YAMLValue,
    l: List[Tuple[YAMLValue, str, int]] = [],
    indent: int = 0,
    partial_key: str = "",
) -> str:
    if isinstance(input, str):
        if "\n" in input:
            return "| \n" + " " * indent + input.replace("\n", "\n" + " " * indent)
        elif '"' not in input:
            return f'"{input}"'
        elif "'" not in input:
            return f"'{input}'"
        else:
            s = input.replace('"', r"\"")
            return f'"{s}"'
    elif isinstance(input, int) or isinstance(input, bool):
        return f"{input}"
    elif isinstance(input, List):
        return yaml_list_to_string(input, l, indent, partial_key)
    elif isinstance(input, Dict):
        return yaml_map_to_string(input, l, indent, partial_key)
    else:
        return ""


def scrub_unused_labels(str_builder: str, l: List[Tuple[YAMLValue, str, int]]) -> str:
    # i = 0
    for v in l:
        if v[2] == 0:
            str_builder = str_builder.replace(f"&{v[1]} ", "")
        # else:
        #     str_builder = str_builder.replace(f"&{v[1]}", f"&{label_name(i)}")
        #     str_builder = str_builder.replace(f"*{v[1]}", f"*{label_name(i)}")
        #     i += 1
    str_builder = re.sub("-\\s*\n\\s*", "- ", str_builder)
    str_builder = re.sub(" +\\n", "\\n", str_builder)
    return str_builder


def dumps(input: YAMLValue) -> str:
    l = []
    s = parent_to_string(input, l, 0)
    return scrub_unused_labels(s, l)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        c = {}
        with open(sys.argv[1], "r") as f:
            c = parse(f.read())
        print(dumps(c).lstrip())
    else:
        print("Please provide a filename as an argument!")
