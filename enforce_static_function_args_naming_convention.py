from common import (
    get_bracket_section,
    comment_remover,
    get_all_static_func_indices,
    args_order_alert,
    check_args,
    check_vars,
)
from enforce_variable_decl_naming_convention import (
    enforce_variable_decl_naming_convention,
)

EXCLUDE = {
}

INCLUDE = {}

ALERT_VAR = "BZG020"
ALERT_CONST = "BZG021"
ALERT_ORDER = "BZG022"
ALERT_ARG = "BZG023"


def enforce_static_function_args_naming_convention(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        data = f.read()

    start_ind = 0
    func_indices = get_all_static_func_indices(data, start_ind)
    for func_ind in func_indices:
        func_decl_line = data[func_ind : data.find("\n", func_ind + 1)]
        # print(func_decl_line)
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

        cnt += check_args(args, ALERT_CONST, file_, func_decl_line, ALERT_ARG)

    return cnt
