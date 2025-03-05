import os.path as osp
from common import (
    get_bracket_section,
    comment_remover,
    is_camel_case,
    args_order_alert,
    check_args,
    check_vars,
    BUILTIN_TYPES,
)
from enforce_variable_decl_naming_convention import (
    enforce_variable_decl_naming_convention,
)
from not_used.enforce_global_func_not_used import GLOBAL_FUNCS_FILE
from not_used.enforce_static_func_not_used import STATIC_FUNCS_FILE
from not_used.enforce_method_not_used import METHODS_FILE
from not_used.enforce_include_not_used import TYPE_FILE


FILE_D = {
    "method": METHODS_FILE,
    "global": GLOBAL_FUNCS_FILE,
    "static": STATIC_FUNCS_FILE,
}

EXCLUDE = {
}

EXCLUDE_CONST = {}

INCLUDE = {}

ALERT_FUNC = "BZG220"
ALERT_ARG = "BZG221"
ALERT_CONST = "BZG222"
ALERT_ORDER = "BZG223"
ALERT_VAR = "BZG224"

TYPES = {
    "void",
    "T",
    "std::string",
    "cv::Rect",
    "cv::Mat",
    "std::vector<std::string>",
    "OutputIterator",
}


def enforce_global_function_args_naming_convention(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        data = f.read()

    start_ind = 0
    func_indices = []

    if osp.exists(TYPE_FILE):
        types = set()
        with open(TYPE_FILE) as f:
            for line in f:
                types.add(line.rstrip("\n").split(" ")[1])

        for t in TYPES.union(BUILTIN_TYPES).union(types):
            func_indices += get_all_global_func_indices(
                data,
                start_ind,
                t,
                file_.endswith(".h"),
            )

    for func_ind in func_indices:
        func_decl_line = data[func_ind : data.find("\n", func_ind + 1)]
        cnt += enforce_function_name(func_decl_line, file_, "global")

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

        while True:
            brackets = get_bracket_section(arg_section, 0, "<>")
            if brackets[0] is None:
                break

            arg_section = (
                arg_section[: brackets[0] - 1] + arg_section[brackets[1] + 1 :]
            )

        args = arg_section.split(",")

        cnt += args_order_alert(args, ALERT_ORDER, file_, func_decl_line)

        if file_ not in EXCLUDE_CONST:
            cnt += check_args(args, ALERT_CONST, file_, func_decl_line, ALERT_ARG)

    return cnt


def enforce_function_name(func_decl_line, file_, type_):
    func_decl_line = func_decl_line.split("(")[0].strip(" \n")
    func_name = func_decl_line.split(" ")[-1].strip("*&")
    if func_name.startswith("operator"):
        return 0

    if func_name == "main":
        return 0

    if "::" in func_name:
        func_name = func_name.split("::")[1]

    if not func_name:
        return 0

    with open(FILE_D[type_], "a") as f:
        f.write(file_ + " " + func_name + "\n")

    if not is_camel_case(func_name) or func_name[0].islower():
        print(f"\n{ALERT_FUNC} : function name should be snake_case")
        print(f'{file_}\n "{func_name}" func name is not CamelCase\n')
        return 1

    return 0


def get_all_global_func_indices(data, start_ind, return_type, is_header):
    func_indices = []
    curr_start_ind = start_ind
    while True:
        while True:
            func_ind = data.find("\n{} ".format(return_type), curr_start_ind)
            if func_ind < 0:
                func_ind = data.find("\ninline {} ".format(return_type), curr_start_ind)
                if func_ind < 0:
                    func_ind = data.find(
                        "\nconstexpr {} ".format(return_type),
                        curr_start_ind,
                    )
                    if func_ind < 0:
                        return func_indices

            next_double_colon_ind = data.find("::", func_ind + len(return_type) + 1)
            next_semicolon_ind = data.find(";", func_ind)
            next_bracket_ind = data.find("(", func_ind)
            if 0 < next_semicolon_ind < next_bracket_ind:
                curr_start_ind = next_semicolon_ind
                continue

            if 0 < next_double_colon_ind < next_bracket_ind:
                curr_start_ind = next_double_colon_ind
                continue

            next_equal_sign_ind = data.find("=", func_ind)
            if 0 < next_equal_sign_ind < next_bracket_ind:
                curr_start_ind = next_equal_sign_ind
                continue

            next_curly_ind = data.find("{", func_ind)
            if not is_header and 0 < next_semicolon_ind < next_curly_ind:
                curr_start_ind = next_semicolon_ind
                continue

            break

        if next_bracket_ind < 0:
            break

        func_indices.append(func_ind)
        curr_start_ind = func_ind + 1

    return func_indices
