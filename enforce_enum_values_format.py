import re
from common import get_bracket_section, comment_remover
from not_used.enforce_enum_vals_not_used import ENUM_VALS_FILE

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG210"


COMPILED1 = re.compile(r"enum class ([a-zA-Z_0-9]+) \{")
COMPILED2 = re.compile(r"enum ([a-zA-Z_0-9]+) \{")


def enforce_enum_values_format(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        data = f.read()

    start_ind = 0
    enum_indices = get_all_enum_indices(data, start_ind)
    for enum_ind, name in enum_indices:
        enum_bracket_indices = get_bracket_section(data, enum_ind, "{}")

        if enum_bracket_indices[0] is None:
            continue

        enum_decl_line = data[enum_bracket_indices[0] : enum_bracket_indices[1]]

        enum_decl_line = comment_remover(enum_decl_line)
        # print(enum_decl_line)

        vals = enum_decl_line.split(",")
        for v in vals:
            v = v.split("=")[0].strip("\n ")
            if not v:
                continue

            with open(ENUM_VALS_FILE, "a") as f:
                if name:
                    f.write(file_ + " " + name + "::" + v + "\n")
                else:
                    f.write(file_ + " " + v + "\n")

            if not v.startswith("k"):
                print(f"\n{ALERT} : variable name should starts with k")
                print(
                    f'{file_}\n{name}::{v}\n "{v}" variable name should starts with k\n',
                )
                cnt += 1

    return cnt


def get_all_enum_indices(data, start_ind):
    enum_indices = []
    curr_start_ind = start_ind
    while True:
        while True:
            srch1 = COMPILED1.search(data[curr_start_ind:])
            srch2 = COMPILED2.search(data[curr_start_ind:])
            if srch1 is None and srch2 is None:
                return enum_indices

            if srch1 is not None:
                enum_ind = srch1.start() + curr_start_ind - 1
                name = srch1.groups(2)[0]
                # print(name)
                break

            enum_ind = srch2.start() + curr_start_ind - 1
            name = ""
            # print(name)
            break

        enum_indices.append((enum_ind, name))
        curr_start_ind = enum_ind + 2
