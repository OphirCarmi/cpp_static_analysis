import re
from common import comment_remover, remove_strings

EXCLUDE = {}

INCLUDE = {}

ALERT = "BZG110"

COMPILED = re.compile(r" / [^k\d+-]+")


def enforce_no_div_by_zero(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    for line in data.splitlines():
        line_wo_s = remove_strings(line)
        match = COMPILED.search(line_wo_s)
        if match is not None:
            print(f"{ALERT}: Maybe div by zero")
            print(f"{file_}\n{line}\n")
            # print(line_wo_s, match.group(0))
            cnt += 1

    return cnt
