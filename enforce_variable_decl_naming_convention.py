import re
from common import (
    get_bracket_section,
    comment_remover,
    get_line_number_of_char_index_in_data,
    whole_word_count,
    BUILTIN_TYPES,
)

from not_used.enforce_variable_not_used import VARS_FILE

EXCLUDE_COUNT = {
}

EXCLUDE_CONST = {
}

EXCLUDE_GLOBAL = {
}

EXCLUDE_MULTIPLE_IN_LINE = {
}

ALERT_NAME = "BZG060"
ALERT_COUNT = "BZG061"
ALERT_CONST = "BZG062"
ALERT_GLOBAL = "BZG063"
ALERT_NOT_INIT = "BZG064"
ALERT_MULTIPLE_IN_LINE = "BZG065"


COMPILED = re.compile(
    r"(\n?[ \t]*(const )?[a-zA-Z0-9_:<>*]+ [*&]?[a-z0-9_:<>]+)",
)

REAL_COMPILED = re.compile(r"^[-+]?[0-9]*\.?[0-9]+(e[-+]?[0-9]+)?;")


def enforce_variable_decl_naming_convention(file_, orig_data, start_ind):
    cnt = 0

    data = comment_remover(orig_data[start_ind:])

    # print("local_hts" in orig_data)
    var_indices = get_all_variable_indices(data, 0)
    for var_ind in var_indices:
        # print("1", data[var_ind + 2:data.find("\n", var_ind + 2)])
        i, line = get_line_number_of_char_index_in_data(data, var_ind)
        var_decl = data[var_ind : data.find("\n", var_ind + 2)]
        # print(var_decl)

        var_decl_split = var_decl.strip(" ").split("=")

        var_decl = var_decl_split[0].strip("\n ")

        if var_decl.startswith("case "):
            continue

        if var_decl.startswith("return "):
            continue

        if var_decl.startswith("static const "):
            continue

        if var_decl.startswith("goto "):
            continue

        # print("3", var_decl)
        triangle_indices = get_bracket_section(var_decl, 0, "<>")
        if triangle_indices[0] is not None:
            var_decl = var_decl[: triangle_indices[0]] + var_decl[triangle_indices[1] :]

        bracket_indices = get_bracket_section(var_decl, 0, "()")
        if bracket_indices[0] is not None:
            var_decl = var_decl[: bracket_indices[0]] + var_decl[bracket_indices[1] :]

        if any(var_decl.startswith(x) for x in ("<< ", "LOG")):
            continue

        if (
            file_ not in EXCLUDE_MULTIPLE_IN_LINE
            and "for (" not in line
            and not var_decl.startswith(":")
            and ") :" not in var_decl
            and ") {" not in var_decl
            and "," in var_decl
            and "&" not in var_decl
            and not var_decl.endswith("{")
            and not file_.endswith(".h")
        ):
            # print(
            #     f"\n{ALERT_MULTIPLE_IN_LINE} : multiple variable declaration in the same line",
            # )
            # print(
            #     f'{file_}:{str(i)}\n{line}\n "{var_decl}" multiple variable declaration in the same line\n',
            # )
            # cnt += 1
            pass

        var_name = var_decl.split("[")[0]
        var_name_s = var_name.split(" ")
        # print(var_name_s)
        var_name = var_name_s[-1]

        has_curly_brackets = "{" in var_name
        var_name = var_name.split("(")[0].split("{")[0]
        var_name = var_name.strip("*&; \n(),")
        if not var_name:
            continue

        if var_name == "nullptr":
            continue

        if var_name.startswith("std::"):
            continue

        var_name = var_name.strip("<>{})")
        if not var_name.strip('"'):
            continue

        if "." in var_name:
            continue

        with open(VARS_FILE, "a") as f:
            f.write(file_ + " " + var_name + "\n")

        if len(var_decl_split) < 2:
            var_type = var_name_s[0].strip(" ")
            # print(var_type)
            if (
                var_type in BUILTIN_TYPES
                and not file_.endswith(".h")
                and not has_curly_brackets
            ):
                print(f"\n{ALERT_NOT_INIT} : variable should be initialized")
                print(
                    f'{file_}:{str(i)}\n{line}\n "{var_name}" variable should be initialized\n',
                )
                cnt += 1
        else:
            if var_decl.startswith("const "):
                curr = var_decl_split[1].strip(" ")
                # TODO(oc): use get_bracket_section instead of curr[0] ...
                if (
                    curr
                    and file_ not in EXCLUDE_GLOBAL
                    and (
                        REAL_COMPILED.search(curr) is not None
                        or (curr[0] == '"' and curr[len(curr) - 1] == '"')
                    )
                ):
                    print(f"\n{ALERT_GLOBAL} : variable should be const global")
                    print(
                        f'{file_}:{str(i)}\n{line}\n "{var_name}" variable should be const global\n',
                    )
                    cnt += 1

        var_name = var_name.strip("{}<>+!")
        if not file_.endswith(".h"):
            if (
                var_name
                and not var_name.startswith("'")
                and not var_name.startswith('"')
                and var_name.strip("0123456789'")
                and "((unused))" not in line
                and "." not in var_name
                and "->" not in var_name
                and "<" not in var_name
                and ("<< " + var_name) not in line
                and not var_name.startswith("k")
                and " return " not in line
                and whole_word_count(var_name, data) < 2
                and file_ not in EXCLUDE_COUNT
            ):
                # print(f"\n{ALERT_COUNT} : variable appears only once")
                # print(
                #     f'{file_}:{str(i)}\n{line}\n "{var_name}" variable appears only once\n',
                # )
                # cnt += 1
                pass

            else:
                # print(data.count(var_decl))
                cnt1 = data.count(var_name + " = ")
                cnt1 += data.count(var_name + " =\n")
                cnt1 += data.count(var_name + "{")
                cnt1 += data.count("&" + var_name)
                cnt1 += data.count("*" + var_name)
                cnt1 += data.count("FILE* " + var_name)
                cnt1 += data.count("DIR* " + var_name)
                cnt1 += data.count(">> " + var_name)
                cnt1 += data.count("+" + var_name)
                cnt1 += data.count(var_name + "+")
                cnt1 += data.count(var_name + " +=")
                cnt1 += data.count(var_name + " |=")
                cnt1 += data.count(var_name + "++")
                cnt1 += data.count(var_name + "--")
                cnt1 += data.count("++" + var_name)
                cnt1 += data.count("--" + var_name)
                cnt2 = data.count(var_name + "[")
                cnt2 += data.count(var_name + "->")
                cnt2 += data.count(var_name + ".")
                cnt2 += data.count(var_name + " <<")
                cnt2 += data.count("std::string " + var_name + ";")
                cnt2 += data.count("cv::Mat " + var_name + ";")

                if (
                    not cnt2
                    and cnt1 < 2
                    and " return " not in line
                    and not any(var_name.startswith(x) for x in "'\"")
                    and not var_name.startswith("k")
                    and not var_decl.startswith("const")
                    and var_name.strip("1234567890")
                    and "for (" not in line
                    and "." not in var_name
                    and "<" not in var_name
                    and not var_decl.endswith(var_name + ";")
                    and "stream " not in var_decl
                    and ("<< " + var_name) not in line
                    and not line.strip(" ").startswith("const")
                    and not data.count("&" + var_name)
                    and not data.count("->" + var_name)
                    and not data.count(var_name + ".")
                    and file_ not in EXCLUDE_CONST
                ):
                    print(f"\n{ALERT_CONST} : variable should be const")
                    print(
                        f'{file_}:{str(i)}\n{line}\n "{var_name}" variable should be const\n',
                    )
                    cnt += 1

        # print("4", var_name)
        if (
            ("<< " + var_name) not in line
            and ("->" + var_name) not in line
            and "suppress " + ALERT_NAME not in line
            and "." not in var_name
            and not var_name.startswith("k")
            and not var_name.startswith("LOG")
            and not var_name.startswith("CV_")
            and var_name != var_name.lower()
        ):
            ind = orig_data.find(line.strip(" "))
            if ind >= 0:
                orig_line = orig_data[ind : orig_data.find("\n", ind)]
                if "suppress " + ALERT_NAME in orig_line:
                    continue

            print(f"\n{ALERT_NAME} : variable name should be snake_case")
            print(
                f'{file_}:{str(i)}\n{line}\n "{var_name}" variable name is not snake_case\n',
            )
            cnt += 1

    return cnt


def get_all_variable_indices(data, start_ind):
    var_indices = []
    curr_start_ind = start_ind
    while True:
        while True:
            # print("a", start_ind, curr_start_ind, data[curr_start_ind:])
            srch = COMPILED.search(data[curr_start_ind:])
            if srch is None:
                return var_indices
            # print("b", srch.group(0))

            var_ind = srch.start() + curr_start_ind
            next_semicolon_ind = data.find(";", var_ind)
            next_equal_ind = data.find("=", var_ind)
            next_open_bracket_ind = data.find("(", var_ind)
            next_close_bracket_ind = data.find(")", var_ind)
            next_open_curly_ind = data.find("{", var_ind)
            next_close_curly_ind = data.find("}", var_ind)
            if 0 < next_semicolon_ind < next_equal_ind:
                if 0 < next_open_bracket_ind < next_semicolon_ind:
                    curr_start_ind = next_open_bracket_ind + 1
                    continue

                if 0 < next_close_bracket_ind < next_semicolon_ind:
                    curr_start_ind = next_close_bracket_ind + 1
                    continue

                if 0 < next_open_curly_ind < next_semicolon_ind:
                    curr_start_ind = next_open_curly_ind + 1
                    continue

                if 0 < next_close_curly_ind < next_semicolon_ind:
                    curr_start_ind = next_close_curly_ind + 1
                    continue

                break

            if 0 < next_open_bracket_ind < next_equal_ind:
                curr_start_ind = next_open_bracket_ind + 1
                continue

            if 0 < next_close_bracket_ind < next_equal_ind:
                curr_start_ind = next_close_bracket_ind + 1
                continue

            if 0 < next_open_curly_ind < next_equal_ind:
                curr_start_ind = next_open_curly_ind + 1
                continue

            if 0 < next_close_curly_ind < next_equal_ind:
                curr_start_ind = next_close_curly_ind + 1
                continue

            break

        var_indices.append(var_ind)
        # print(srch.group(0))
        curr_start_ind = var_ind + len(srch.group(0))
