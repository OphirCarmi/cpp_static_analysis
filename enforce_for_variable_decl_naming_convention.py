import re
from common import get_bracket_section, get_line_number_of_char_index, BUILTIN_TYPES

EXCLUDE = {}

INCLUDE = {}

ALERT_NAME = "BZG050"
ALERT_CONST = "BZG051"


COMPILED = re.compile(r"  for \(")
COMPILED_CONST = re.compile(r"const ([a-zA-Z0-9:_<>]+) [^&]")


def enforce_for_variable_decl_naming_convention(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        data = f.read()

    start_ind = 0
    for_loop_indices = get_all_for_loop_indices(data, start_ind)
    for for_loop_ind in for_loop_indices:
        i, line = get_line_number_of_char_index(file_, for_loop_ind)
        for_bracket_indices = get_bracket_section(data, for_loop_ind, "()")

        if for_bracket_indices[0] is None:
            continue

        for_decl_line = data[for_bracket_indices[0] : for_bracket_indices[1]]
        if for_decl_line.count(";"):
            names = regular_for(for_decl_line)

        else:
            names, num_err = foreach(file_, i, line, for_decl_line)
            cnt += num_err

        # print(names)
        for name in names:
            if not name.islower():
                print(f"\n{ALERT_NAME} : variable name should be snake_case")
                print(
                    f'{file_}:{str(i)}\n{line}\n "{name}" variable name is not snake_case\n',
                )
                cnt += 1

    return cnt


def foreach(file_, i, line, for_decl_line):
    first_section = for_decl_line.split(":")[0].strip(" ")
    err = False
    match = COMPILED_CONST.search(for_decl_line)
    if match is not None and match.group(1) not in BUILTIN_TYPES:
        print(f"\n{ALERT_CONST} : const auto should be ref")
        print(
            f"{file_}:{str(i)}\n{line}\n add & please\n",
        )
        err = True

    name = first_section.split(" ")[-1].strip("*&")
    return [name], err


def regular_for(for_decl_line):
    names = []
    first_section = for_decl_line.split(";")[0].strip(" ")
    if not first_section:
        return names

    bracket_inds = get_bracket_section(first_section, 0, "()")
    if bracket_inds[0]:
        first_section = (
            first_section[: bracket_inds[0]] + first_section[bracket_inds[1] :]
        )

    bracket_inds = get_bracket_section(first_section, 0, "{}")
    if bracket_inds[0]:
        first_section = (
            first_section[: bracket_inds[0]] + first_section[bracket_inds[1] :]
        )

    vars_ = first_section.split(",")
    for v in vars_:
        name = v.split("=")[0].strip(" ").split(" ")[-1].strip("*&")
        names.append(name)

    return names


def get_all_for_loop_indices(data, start_ind):
    for_loop_indices = []
    curr_start_ind = start_ind
    while True:
        while True:
            srch = COMPILED.search(data[curr_start_ind:])
            if srch is None:
                return for_loop_indices

            for_loop_ind = srch.start() + curr_start_ind - 1
            break

        for_loop_indices.append(for_loop_ind)
        curr_start_ind = for_loop_ind + 2
