import re
from common import (
    get_bracket_section,
    comment_remover,
    is_camel_case,
    examine_args,
    get_line_number_of_char_index,
    BUILTIN_TYPES,
)
from not_used.enforce_member_variable_not_used import MEMBER_VARS_FILE

EXCLUDE = {
}

EXCLUDE_NO_PRIVATE = {}

INCLUDE = {}

ALERT_VAR = "BZG001"
ALERT_METHOD = "BZG002"
ALERT_CLASS = "BZG003"
ALERT_ARG = "BZG004"
ALERT_NO_PRIVATE = "BZG005"
ALERT_PRIVATE_IN_STRUCT = "BZG006"
ALERT_PRIVATE_PUBLIC_ORDER = "BZG007"


def camel_to_snake(s):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")


def enforce_member_variables_naming_convention(file_):
    tot = 0
    tot += enforce_member_variables_naming_convention_per_type(file_, "class")
    tot += enforce_member_variables_naming_convention_per_type(file_, "struct")
    tot += enforce_member_variables_naming_convention_per_type(file_, "enum")
    return tot


def enforce_member_variables_naming_convention_per_type(file_, type_str):
    if file_ in EXCLUDE:
        return 0

    if INCLUDE and file_ not in INCLUDE:
        return 0

    # print(type_str, file_)
    with open(file_) as f:
        data = f.read()

    start_ind = 0

    class_indices = []
    while True:
        while True:
            class_ind = -1
            srch = re.search(r"\n[\t ]*" + type_str + " [A-Za-z_0-9]", data[start_ind:])
            if srch is None:
                break

            class_ind = srch.start() + start_ind
            next_curly_ind = data.find("{", class_ind)
            if next_curly_ind < 0:
                class_ind = -1
                break

            next_semicolon_ind = data.find(";", class_ind)
            if next_semicolon_ind > 0 and next_semicolon_ind < next_curly_ind:
                start_ind = next_semicolon_ind
                continue

            next_semicolon_ind = data.find("(", class_ind)
            if next_semicolon_ind > 0 and next_semicolon_ind < next_curly_ind:
                start_ind = next_semicolon_ind
                continue

            next_equal_ind = data.find("=", class_ind)
            if next_equal_ind > 0 and next_equal_ind < next_curly_ind:
                start_ind = next_equal_ind
                continue

            break

        if class_ind < 0:
            break

        class_indices.append(class_ind)
        start_ind = class_ind + 1

    errors = 0
    for ind in class_indices:
        if type_str != "enum":
            errors += process_curly_section(data, ind, type_str, file_)

        errors += process_class_name(data, ind, file_)

    return errors


def process_curly_section(data, class_ind, type_str, file_):
    cnt = 0
    class_decl_indices = get_bracket_section(data, class_ind, "{}")
    if class_decl_indices[0] is None:
        return cnt

    class_decl = data[class_decl_indices[0] : class_decl_indices[1]]
    if type_str == "class":
        if class_decl.count("private:") == 0:
            if class_decl.count("protected:") == 0 and file_ not in EXCLUDE_NO_PRIVATE:
                line = get_line_number_of_char_index(file_, class_decl_indices[0])[0]
                print(f"{ALERT_NO_PRIVATE}: no private section in class")
                print(f"{file_}:{str(line)}\n")
                cnt += 1
        elif class_decl.count("public:") and class_decl.index(
            "private:",
        ) < class_decl.index("public:"):
            line = get_line_number_of_char_index(file_, class_decl_indices[0])[0]
            print(
                f"{ALERT_PRIVATE_PUBLIC_ORDER}: private section before public section class",
            )
            print(f"{file_}:{str(line)}\n")
            cnt += 1

    if type_str == "struct" and class_decl.count("private:"):
        line = get_line_number_of_char_index(file_, class_decl_indices[0])[0]
        print(f"{ALERT_PRIVATE_IN_STRUCT}: private section in struct")
        print(f"{file_}:{str(line)}\n")
        cnt += 1

    # print(class_decl)
    curr_data = clear_method_def(class_decl)
    curr_data = clear_ifdef(curr_data)

    classified = classify_to_vars_methods(curr_data)
    wrong_method_names = methods_in_wrong_naming(classified, file_)
    wrong_arg_names = args_in_wrong_naming(classified)
    wrong_var_names = vars_in_wrong_naming(classified, type_str, file_)
    if not wrong_var_names and not wrong_method_names and not wrong_arg_names:
        return cnt

    cnt += alert_vars(wrong_var_names, class_decl, class_decl_indices, file_, type_str)
    cnt += alert_methods(wrong_method_names, class_decl, class_decl_indices, file_)
    cnt += alert_args(wrong_arg_names, class_decl, class_decl_indices, file_)

    return cnt


def process_class_name(data, class_ind, file_):
    class_decl = data[class_ind : data.find("\n", class_ind + 1)]
    if f"suppress {ALERT_CLASS}" in class_decl:
        return 0

    class_name = class_decl.strip("\n").split("{")[0]
    class_name = class_name.strip("\n").split(":")[0]
    class_name = class_name.strip().split(" ")[-1]
    if class_name and (not is_camel_case(class_name) or class_name[0].islower()):
        line = get_line_number_of_char_index(file_, class_ind)[0]
        print(f"{ALERT_CLASS}: Type name should be CamelCase")
        print(f'{file_}:{str(line)} change "{class_name}"\n')
        return 1

    return 0


def classify_to_vars_methods(curr_data):
    curr_data = comment_remover(curr_data)
    all_members = [
        x.strip()
        for x in curr_data.replace("\n", "")
        .replace("{}", ";")
        .replace("private:", "")
        .replace("public:", "")
        .replace("protected:", "")
        .split(";")
    ]
    all_members = [x for x in all_members if x]
    types = [0 if "(" in x.split("=")[0] else 1 for x in all_members]
    return list(zip(types, all_members))


def methods_in_wrong_naming(classified, file_):
    names = []
    methods = [x[1] for x in classified if not x[0]]
    for full_decl in methods:
        method_name = full_decl.split("=")[0]
        method_name = method_name.strip().split("(")[0]
        method_name = method_name.strip().split(" ")[-1]
        method_name = method_name.strip("&*")
        if method_name.startswith("operator"):
            continue

        if method_name.startswith("for"):
            continue

        if method_name.startswith("FRIEND_TEST"):
            continue

        if method_name in BUILTIN_TYPES:
            continue

        if not method_name.startswith("~"):
            with open("/tmp/methods.txt", "a") as f:
                f.write(file_ + " " + method_name + "\n")

        if not is_camel_case(method_name) or method_name[0].islower():
            names.append((method_name, full_decl))

    return names


def args_in_wrong_naming(classified):
    tot = []
    methods = [x[1] for x in classified if not x[0]]
    for full_decl in methods:
        if "operator" in full_decl:
            continue

        if "FRIEND_TEST" in full_decl:
            continue

        arg_indices = get_bracket_section(full_decl, 0, "()")
        if arg_indices[0] is None:
            continue

        names = examine_args(full_decl, full_decl, arg_indices)
        tot += names

    return tot


def vars_in_wrong_naming(classified, type_str, file_):
    names = []
    vars_ = [x[1] for x in classified if x[0]]
    for full_decl in vars_:
        # print(full_decl)
        partial_decl = full_decl
        _, end_bracket = get_bracket_section(partial_decl, 0, "<>")
        if end_bracket is not None:
            partial_decl = partial_decl[end_bracket + 1 :]

        for v in partial_decl.split(","):
            if "operator=(" in v:
                continue

            if "=" in v:
                v = v.split("=")[0]

            var_name = v
            if "[]" not in var_name:
                var_name = var_name.split("[")[0]

            if var_name.startswith("enum class"):
                continue

            if var_name.startswith("typedef"):
                continue

            if var_name.startswith("inline"):
                continue

            if var_name.startswith("::"):
                continue

            if var_name.startswith("struct") and var_name.count(" ") == 1:
                continue

            var_name = var_name.strip().split(" ")[-1].strip("*&")
            with open(MEMBER_VARS_FILE, "a") as f:
                f.write(file_ + " " + var_name + "\n")

            if (
                not var_name.islower()
                or type_str == "class"
                and not var_name.endswith("_")
            ):
                names.append((var_name, full_decl))

    return names


def alert_vars(wrong_var_names, class_decl, class_decl_indices, file_, type_str):
    _cnt = 0
    for _cnt, (var_name, full_decl) in enumerate(wrong_var_names):
        # print(full_decl)
        full_decl_ind = class_decl.find(full_decl)
        ind = full_decl_ind + class_decl_indices[0]
        line = get_line_number_of_char_index(file_, ind)[0]
        print(
            f"{ALERT_VAR}: Member variable name should be snake_case with trailing underscore",
        )
        end_str = "_" if type_str == "class" else ""
        print(
            f'{file_}:{str(line)} change "{var_name}" to "{camel_to_snake(var_name)}{end_str}"\n',
        )

    return _cnt


def alert_methods(wrong_method_names, class_decl, class_decl_indices, file_):
    _cnt = 0
    for _cnt, (method_name, full_decl) in enumerate(wrong_method_names):
        # print(full_decl)

        full_decl_ind = class_decl.find(full_decl)
        ind = full_decl_ind + class_decl_indices[0]
        i, line = get_line_number_of_char_index(file_, ind)
        if f"suppress {ALERT_METHOD}" in line:
            continue

        print(f"{ALERT_METHOD}: Member method name should be CamelCase")
        print(f'{file_}:{str(i)}\n{line}\n change "{method_name}"\n')

    return _cnt


def alert_args(wrong_arg_names, class_decl, class_decl_indices, file_):
    cnt = 0
    for arg_name, full_decl in wrong_arg_names:
        # print(full_decl)
        full_decl_ind = class_decl.find(full_decl)
        ind = full_decl_ind + class_decl_indices[0]
        line = get_line_number_of_char_index(file_, ind)[0]
        if arg_name.startswith("k") and arg_name[1].isupper():
            continue

        if arg_name.startswith("std::"):
            continue

        print(f"{ALERT_ARG}: argument name should be snake_case")
        print(
            f'{file_}:{str(line)}\n change "{arg_name}" to "{camel_to_snake(arg_name)}"\n',
        )
        cnt += 1

    return cnt


def clear_ifdef(curr_data):
    lines = curr_data.splitlines()
    filtered = []
    for line in lines:
        if not any(line.startswith(x) for x in ("#if", "#endif")):
            filtered.append(line)

    return "\n".join(filtered)


def clear_method_def(curr_data):
    curr_ind = 0
    while True:
        method_decl = get_bracket_section(curr_data, curr_ind, "{}")
        if method_decl[0] is None:
            break

        curr_data = curr_data[: method_decl[0]] + curr_data[method_decl[1] :]
        curr_ind = method_decl[0] + 1

    # print(curr_data)
    return curr_data
