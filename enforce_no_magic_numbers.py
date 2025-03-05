import re
from common import comment_remover, remove_strings

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG100"

COMPILED = re.compile(r"\b\d+\.?\d*\b")
COMPILED_ENUM = re.compile(r"  k[A-Z][A-Za-z0-9]+ = \d+\.?\d*,?")


def enforce_no_magic_numbers(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    in_const = False
    for line in data.splitlines():
        if line.startswith("// "):
            continue

        if any(
            line.startswith(x)
            for x in (
                "static const ",
                "const ",
                "static constexpr ",
                "constexpr ",
                "enum class ",
            )
        ):
            in_const = True

        if in_const:
            if ";" in line:
                in_const = False

            continue

        if COMPILED_ENUM.search(line) is not None:
            continue

        line_wo_s = remove_strings(line)
        match = COMPILED.search(line_wo_s)
        if match is not None:
            if any(float(match.group(0)) == x for x in (0, 1, -1)):
                continue

            print(f"{ALERT}: Please don't use magic numbers")
            print(f"{file_}\n{line}\n")
            # print(line_wo_s, match.group(0))
            cnt += 1

    return cnt
