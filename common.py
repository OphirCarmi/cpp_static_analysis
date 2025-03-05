import re

BUILTIN_TYPES = {
    "bool",
    "double",
    "float",
    "int8_t",
    "uint8_t",
    "int16_t",
    "uint16_t",
    "int",
    "uint32_t",
    "int64_t",
    "uint64_t",
    "char",
    "size_t",
    "ssize_t",
}

COMPILED = re.compile(
    r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
    re.DOTALL | re.MULTILINE,
)

SUB_IFDEF = re.compile(r"\n#.*\n")
SUB_SPACES = re.compile(r"\s*\n\s*\n")
SUB_DOUBLE_BACKSLASH = re.compile(r"\\")

EXCLUDE_POINTER = {
}

ALERT_POINTER = "BZG460"


def is_camel_case(s):
    return s != s.lower() and s != s.upper() and "_" not in s


def comment_remover(data, *, remove_ifdef=True):
    def replacer(match):
        s = match.group(0)
        if s.startswith("/"):
            return " "  # note: a space and not an empty string

        return s

    data = COMPILED.sub(replacer, data)

    if remove_ifdef:
        data = SUB_IFDEF.sub("\n", data)

    data = SUB_SPACES.sub("\n", data)
    data = SUB_DOUBLE_BACKSLASH.sub("", data)

    data = remove_strings(data)

    return data  # noqa: R504, PIE781


def remove_strings(s):
    is_in = False
    last_c = ""
    new_s = ""
    for c in s:
        if last_c and last_c != "\\" and c == '"':
            is_in = not is_in

        if not is_in:
            new_s += c

        last_c = c

    return new_s


def get_bracket_section(data, start, brackets):
    start_class_ind = data.find(brackets[0], start)
    if start_class_ind < 0:
        return None, None

    curr_ind = start_class_ind
    cnt = 1
    while True:
        left = data.find(brackets[0], curr_ind + 1)
        right = data.find(brackets[1], curr_ind + 1)
        if left < 0:
            if right < 0:
                return None, None

            min_ = right

        elif right < 0:
            min_ = left

        else:
            min_ = min((left, right))

        if data[min_] == brackets[0]:
            cnt += 1

        elif data[min_] == brackets[1]:
            cnt -= 1

        curr_ind = min_
        if not cnt:
            break

    return start_class_ind + 1, curr_ind


def get_all_static_func_indices(data, start_ind):
    func_indices = []
    curr_start_ind = start_ind
    while True:
        while True:
            func_ind = data.find("\nstatic ", curr_start_ind)
            if func_ind < 0:
                return func_indices

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

            break

        if next_bracket_ind < 0:
            break

        func_indices.append(func_ind)
        curr_start_ind = func_ind + 1

    return func_indices


def examine_args(data, full_decl, arg_indices):
    args_signature = data[arg_indices[0] : arg_indices[1]]
    if not args_signature:
        return []

    # print("args_signature", args_signature)
    args = args_signature.split(",")
    names = []
    for arg in args:
        arg = arg.strip(" ")
        arg = arg.split(" = ")[0]
        arg = arg.split(" ")[-1]
        arg = arg.strip("&*[]")
        # with open("/tmp/args.txt", "a") as f:
        #     f.write(arg + "\n")

        if arg.isdigit():
            continue

        if not arg.islower():
            names.append((arg, full_decl))

    return names


# TODO(oc): calc multiple indices in the same file read
def get_line_number_of_char_index(file_, ind):
    if ind < 0:
        return -1, None

    cnt = 0
    with open(file_) as f:
        for i, line in enumerate(f):
            cnt += len(line)
            if cnt > ind:
                return i + 1, line

    return -2, None


def get_line_number_of_char_index_in_data(data, ind):
    if ind < 0:
        return -1, None

    cnt = 0
    for i, line in enumerate(data.splitlines()):
        cnt += len(line) + 1
        if cnt > ind:
            return i + 1, line

    return -2, None


def args_order_alert(args, alert, file_, func_decl_line):
    cnt = 0
    no_default_vals = []
    for arg in args:
        no_default_vals.append(arg.split(" =")[0].split(" ")[-1])

    is_output = ["*" in x for x in no_default_vals[::-1]]
    found_input = False
    for is_o in is_output:
        if not is_o:
            found_input = True
            continue

        if found_input and is_o:
            print(f"\n{alert} : order of args should be input and then output")
            print(f"{file_}:\n {func_decl_line}\n")
            cnt += 1

    return cnt


def check_args(args, alert_const, file_, func_decl_line, alert_name):
    cnt = 0
    for arg in args:
        # print(arg)
        arg = arg.strip(" ")
        if any(arg.startswith(x) for x in BUILTIN_TYPES) and all(
            x not in arg for x in ("*", "const", "&", "[")
        ):
            print(f"\n{alert_const} : arg should be const")
            print(f'{file_}:\n "{arg}" arg is not const\n')
            cnt += 1

        arg_name = arg.split(" ")[-1].strip("*&\n[]- ")

        if (
            "*" in arg
            and file_ not in EXCLUDE_POINTER
            and arg_name != "argv"
            and not (
                arg_name.startswith("k") and len(arg_name) > 1 and arg_name[1].isupper()
            )
            and not arg_name.startswith("static_cast<")
        ):
            print(f"\n{ALERT_POINTER} : no passing by pointer")
            print(f'{file_}:\n {arg}\n"{arg_name}" arg is a pointer\n')
            cnt += 1

        # print(arg_name)
        if not arg_name:
            continue

        if arg_name.isdigit():
            continue

        if arg_name.startswith("std::"):
            continue

        if arg_name.startswith("static_cast<"):
            continue

        if arg_name.startswith("k") and arg_name[1].isupper():
            continue

        if arg_name != arg_name.lower():
            print(f"\n{alert_name} : arg name should be snake_case")
            print(
                f'{file_}:\n "{arg_name}" arg name is not snake_case\n',
            )
            cnt += 1

    return cnt


def check_vars(body_section, alert, file_):
    cnt = 0
    for line in body_section.splitlines():
        if line.startswith("static const"):
            continue

        if not any(x in line for x in "=("):
            continue

        split = (
            line.strip(" ")
            .split("[")[0]
            .strip(" ")
            .split("(")[0]
            .strip(" ")
            .split("=")[0]
            .strip(" ")
        )
        if any(x in split for x in ("<<", ".", "{", "#", "return")):
            continue

        parts = split.split(" ")
        if len(parts) > 1:
            name = parts[-1].split("[")[0]
            if not name.strip("+-!|\"%*&<>'"):
                continue

            if name.startswith("cv::"):
                continue

            if name != name.lower():
                print(f"\n{alert} : var name should be snake_case")
                print(f'{file_}:{line}\n "{name}" var name is not snake_case\n')
                cnt += 1

    return cnt


def whole_word_find(substr, string):
    return whole_word_count(substr, string) > 0


def whole_word_count(substr, string):
    return len(re.findall(r"\b" + re.escape(substr) + r"\b", string))
