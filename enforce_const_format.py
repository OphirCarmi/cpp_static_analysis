from common import comment_remover, get_bracket_section, whole_word_count, BUILTIN_TYPES
from not_used.enforce_static_const_not_used import STATIC_CONST_FILE

EXCLUDE = {
}

INCLUDE = {}

ALERT_FORMAT = "BZG120"
ALERT_CONSTEXPR = "BZG121"
ALERT_UNUSED = "BZG122"


def enforce_const_format(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    names = []
    with open(file_) as f:
        for i, line in enumerate(f):
            line_wo_comment = comment_remover(line)
            if line_wo_comment.startswith("static const "):
                names, c = found(
                    line_wo_comment,
                    names,
                    i,
                    line,
                    file_,
                    "static const ",
                )
                cnt += c

            elif line_wo_comment.startswith("static constexpr "):
                names, c = found(
                    line_wo_comment,
                    names,
                    i,
                    line,
                    file_,
                    "static constexpr ",
                )
                cnt += c

            elif file_.endswith(".h") and line_wo_comment.startswith("constexpr "):
                names, c = found(line_wo_comment, names, i, line, file_, "constexpr ")
                cnt += c

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)

    for i, _, line, name in names:
        if (
            (not name.startswith("k") or name[1].islower())
            and not name.startswith("operator")
            and not line.endswith("{\n")
        ):
            print(f"\n{ALERT_FORMAT} : var name should be in kConstVar format")
            print(
                f'{file_}:{str(i + 1)}\n{line}\n "{name}" is not in kConstVar format\n',
            )
            cnt += 1

        if file_.endswith(".cpp"):
            usages = (
                whole_word_count(name, data)
                - data.count(" " + name + " = ")
                - data.count(" " + name + " =\n")
            )
            name = name.strip("[]")
            if not name:
                continue

            if not usages:
                print(f"\n{ALERT_UNUSED} : var is unused")
                print(f'{file_}:{str(i + 1)}\n{line}\n "{name}" is not in use\n')
                cnt += 1

        else:
            if name.startswith("operator"):
                continue

            with open(STATIC_CONST_FILE, "a") as f:
                f.write(file_ + " " + name + "\n")

    return cnt


def found(line_wo_comment, names, i, line, file_, expression):
    cnt = 0
    line_wo_comment = line_wo_comment.split(expression)[1]
    bracket_inds = get_bracket_section(line_wo_comment, 0, "<>")
    if bracket_inds[0]:
        line_wo_comment = (
            line_wo_comment[: bracket_inds[0]] + line_wo_comment[bracket_inds[1] :]
        )

    name = line_wo_comment.split(" ")

    if name[0] in ("struct", "enum"):
        name = name[2:]

    else:
        if (
            name[0] in BUILTIN_TYPES
            and "[" not in name[1]
            and expression == "static const "
        ):
            curr = name[1].strip("*;\n[]{")
            print(f"\n{ALERT_CONSTEXPR} : var should be constexpr")
            print(f'{file_}:{str(i + 1)}\n{line}\n "{curr}" is not constexpr\n')
            cnt += 1

        name = name[1:]

    name = name[0].strip("*;\n[]{")

    if not name or name == "=":
        return names, cnt

    name = name.split("(")[0].split("{")[0]
    names.append((i, file_, line, name))
    return names, cnt
