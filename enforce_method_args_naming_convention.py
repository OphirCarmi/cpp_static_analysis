import re
from common import (
    get_bracket_section,
    comment_remover,
    is_camel_case,
    args_order_alert,
    check_args,
    check_vars,
)
from enforce_variable_decl_naming_convention import (
    enforce_variable_decl_naming_convention,
)
from not_used.enforce_method_not_used import METHODS_FILE


EXCLUDE = {
}

EXCLUDE_CONST = {
}

INCLUDE = {}

ALERT_FUNC = "BZG200"
ALERT_ARG = "BZG201"
ALERT_CONST = "BZG202"
ALERT_ORDER = "BZG203"
ALERT_VAR = "BZG204"


def enforce_method_args_naming_convention(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        data = f.read()

    start_ind = 0
    func_indices = get_all_method_indices(data, start_ind)
    for func_ind in func_indices:
        func_decl_line = data[func_ind : data.find("\n", func_ind + 1)]
        # print("aa", func_decl_line)
        cnt += enforce_function_name(func_decl_line, file_)

        body_section_indices = get_bracket_section(data, func_ind, "{}")
        if body_section_indices[0] is None:
            continue

        body_section = comment_remover(
            data[body_section_indices[0] : body_section_indices[1]],
        )

        cnt += check_vars(body_section, ALERT_VAR, file_)

        arg_section_indices = get_bracket_section(data, func_ind, "()")
        if arg_section_indices[0] is None:
            continue

        cnt += enforce_variable_decl_naming_convention(
            file_,
            data,
            arg_section_indices[1],
        )
        arg_section = comment_remover(
            data[arg_section_indices[0] : arg_section_indices[1]],
        )

        if " " not in arg_section:
            continue

        args = arg_section.split(",")
        cnt += args_order_alert(args, ALERT_ORDER, file_, func_decl_line)

        if file_ not in EXCLUDE_CONST:
            cnt += check_args(args, ALERT_CONST, file_, func_decl_line, ALERT_ARG)

    return cnt


def get_all_method_indices(data, start_ind):
    func_indices = []
    curr_start_ind = start_ind
    while True:
        while True:
            srch = re.search(
                r"\n[A-Za-z_0-9:]+ [A-Za-z_0-9]+::[A-Za-z_0-9]+",
                data[curr_start_ind:],
            )
            if srch is None:
                method_ind = -1
                break

            method_ind = srch.start() + curr_start_ind
            next_bracket_ind = data.find("(", method_ind)
            if next_bracket_ind < 0:
                return func_indices

            next_using_ind = data.find("using", method_ind)
            next_space_ind = data.find(" ", method_ind)
            if 0 < next_using_ind < next_space_ind:
                curr_start_ind = next_space_ind
                continue

            next_inline_ind = data.find("inline", method_ind)
            next_space_ind = data.find(" ", method_ind)
            if 0 < next_inline_ind < next_space_ind:
                curr_start_ind = next_space_ind
                continue

            next_semicolon_ind = data.find(";", method_ind)
            if 0 < next_semicolon_ind < next_bracket_ind:
                curr_start_ind = next_semicolon_ind
                continue

            next_equal_sign_ind = data.find("=", method_ind)
            if 0 < next_equal_sign_ind < next_bracket_ind:
                curr_start_ind = next_equal_sign_ind
                continue

            next_curly_ind = data.find("{", method_ind)
            if 0 < next_semicolon_ind < next_curly_ind:
                curr_start_ind = next_semicolon_ind
                continue

            break

        if method_ind < 0:
            break

        func_indices.append(method_ind)
        curr_start_ind = method_ind + 1

    return func_indices


def enforce_function_name(func_decl_line, file_):
    func_decl_line = func_decl_line.split("(")[0].strip(" \n")
    func_name = func_decl_line.split(" ")[-1].strip("*&{").split("::")[-1]
    if func_name.startswith("operator"):
        return 0

    if func_name.startswith("k"):
        return 0

    if func_name == "main":
        return 0

    with open(METHODS_FILE, "a") as f:
        f.write(file_ + " " + func_name + "\n")

    if not is_camel_case(func_name) or func_name[0].islower():
        print(f"\n{ALERT_FUNC} : function name should be snake_case")
        print(f'{file_}\n "{func_name}" func name is not CamelCase\n')
        return 1

    return 0
