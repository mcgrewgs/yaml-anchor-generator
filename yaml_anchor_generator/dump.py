from typing import Any, Dict, List, Tuple, Union
from yaml import full_load as parse
import re
import sys

INDENT_INC = 2

YAMLValue = Union[int, bool, str, List[Any], Dict[str, Any]]


def label_name(partial_key: str) -> str:
    k = re.sub("[^a-zA-Z0-9]+", "_", partial_key)
    return f"label{k}"


def dict_contains(parent: Any, child: Any) -> bool:
    if isinstance(parent, Dict) and isinstance(child, Dict):
        for k in child:
            if k not in parent:
                return False

    return True


def same_type(a: Any, b: Any) -> bool:
    return type(a) == type(b)


def count_overlap(parent: Any, child: Any) -> int:
    overlap = 0
    if isinstance(parent, Dict) and isinstance(child, Dict):
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
                    t = labels[best_label_index][0]
                    if isinstance(t, Dict):
                        for kk, vv in v.items():
                            if kk not in t or t[kk] != vv:
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
                    t = labels[best_label_index][0]
                    if isinstance(t, Dict):
                        for kk, vv in v.items():
                            if kk not in t or t[kk] != vv:
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
    current_labels: List[Tuple[YAMLValue, str, int]] = [],
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
        return yaml_list_to_string(input, current_labels, indent, partial_key)
    elif isinstance(input, Dict):
        return yaml_map_to_string(input, current_labels, indent, partial_key)
    else:
        return ""


def scrub_unused_labels(
    str_builder: str,
    current_labels: List[Tuple[YAMLValue, str, int]],
    interactive: bool = False,
) -> str:
    for v in current_labels:
        if v[2] == 0:
            str_builder = str_builder.replace(f"&{v[1]} ", "")
        elif interactive:
            prompt = f"The value {v[0]} was found {v[2] + 1} times in the input YAML file; what label would you like to use for it?  Provide an empty string to use the auto-generated label {v[1]}\n"
            new_name = input(prompt)

            if new_name is not None and new_name != "":
                str_builder = str_builder.replace(f"&{v[1]}", f"&{new_name}")
                str_builder = str_builder.replace(f"*{v[1]}", f"*{new_name}")
    str_builder = re.sub("-\\s*\n\\s*", "- ", str_builder)
    str_builder = re.sub(" +\\n", "\\n", str_builder)
    return str_builder


def dumps(input: YAMLValue, interactive: bool = False) -> str:
    current_labels: List[Tuple[YAMLValue, str, int]] = []
    s = parent_to_string(input, current_labels, 0)
    return scrub_unused_labels(s, current_labels, interactive)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        i = 1
        interactive = False
        if sys.argv[1] == "-i" or sys.argv[1] == "--interactive":
            i += 1
            interactive = True
        c = {}
        with open(sys.argv[i], "r") as f:
            c = parse(f.read())
        o = dumps(c, interactive).lstrip()
        with open(sys.argv[i + 1], "w") as f:
            f.write(o)
        # if interactive:
        #     print(o)
    else:
        print("Please provide input and output filenames as arguments!")
