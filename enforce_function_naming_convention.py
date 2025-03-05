import re
from common import is_camel_case, comment_remover, get_bracket_section, examine_args
from enforce_variable_decl_naming_convention import (
    enforce_variable_decl_naming_convention,
)


EXCLUDE = {
}

INCLUDE = {}

ALERT_FUNC = "BZG040"
ALERT_ARG = "BZG041"


COMPILED = re.compile(r"\n([A-Za-z0-9_:<>]+) ")


def enforce_function_naming_convention(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    with open(file_) as f:
        data = f.read()

    start_ind = 0
    data = comment_remover(data)
    func_indices = get_all_func_indices(data, start_ind)
    for func_ind in func_indices:
        func_decl_line = data[func_ind : data.find("\n", func_ind + 1)]
        arg_section_indices = get_bracket_section(data, func_ind, "()")

        if arg_section_indices[0] is None:
            continue

        cnt += enforce_variable_decl_naming_convention(
            file_,
            data,
            arg_section_indices[1],
        )
        cnt += enforce_function_name(func_decl_line, file_)
        cnt += enforce_arg_name(data, func_ind, func_decl_line, file_)

    return cnt


def enforce_arg_name(data, func_ind, func_decl_line, file_):
    arg_indices = get_bracket_section(data, func_ind, "()")
    # print("a", data[arg_indices[0]: arg_indices[1]])
    if arg_indices[0] is None:
        return 0

    names = examine_args(data, func_decl_line, arg_indices)
    for name, _ in names:
        print(f"\n{ALERT_ARG} : function name should be snake_case")
        print(f'{file_}\n "{name}" arg name is not snake_case\n')

    return len(names)


def enforce_function_name(func_decl_line, file_):
    func_decl_line = func_decl_line.split("(")[0].strip(" \n")
    func_name = func_decl_line.split(" ")[-1].strip("*&").split("::")[-1]
    if func_name.startswith("operator"):
        return 0

    if func_name == "main":
        return 0

    # with open(FUNCS_FILE, "a") as f:
    # f.write(file_ + " " + func_name + "\n")
    if not is_camel_case(func_name) or func_name[0].islower():
        print(f"\n{ALERT_FUNC} : function name should be CamelCase")
        print(f'{file_}\n "{func_name}" func name is not CamelCase\n')
        return 1

    return 0


def get_all_func_indices(data, start_ind):
    func_indices = []
    curr_start_ind = start_ind
    while True:
        next_bracket_ind = -1
        while True:
            srch = COMPILED.search(data[curr_start_ind:])
            if srch is None:
                return func_indices

            if srch.group(1) == "class":
                curr_start_ind += len("class") + 1
                continue

            if srch.group(1) == "struct":
                curr_start_ind += len("struct") + 1
                continue

            if srch.group(1) == "static":
                curr_start_ind += len("static") + 1
                continue

            if srch.group(1) == "enum":
                curr_start_ind += len("enum") + 1
                continue

            if srch.group(1) == "namespace":
                curr_start_ind += len("namespace") + 1
                continue

            if srch.group(1) == "typedef":
                curr_start_ind += len("typedef") + 1
                continue

            if srch.group(1) == "extern":
                curr_start_ind += len("extern") + 1
                continue

            func_ind = srch.start() + curr_start_ind
            # print("3", data[func_ind:func_ind + 20])
            next_semicolon_ind = data.find(";", func_ind)
            next_bracket_ind = data.find("(", func_ind)
            if 0 < next_semicolon_ind < next_bracket_ind:
                curr_start_ind = next_semicolon_ind
                continue

            next_equal_sign_ind = data.find("=", func_ind)
            if 0 < next_equal_sign_ind < next_bracket_ind:
                curr_start_ind = next_equal_sign_ind
                continue

            next_curly_ind = data.find("{", func_ind)
            if 0 < next_semicolon_ind < next_curly_ind:
                curr_start_ind = next_semicolon_ind
                continue

            # print("4", data[func_ind:func_ind + 20])
            break

        if next_bracket_ind < 0:
            break

        func_indices.append(func_ind)
        curr_start_ind = func_ind + 1

    return func_indices
