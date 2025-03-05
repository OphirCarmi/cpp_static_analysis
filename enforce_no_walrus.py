import re
from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG410"

COMPILED = re.compile(r"if \([^=\)]+ = ")


def enforce_no_walrus(file_):
    if file_ in EXCLUDE:
        return 0

    if INCLUDE and file_ not in INCLUDE:
        return 0

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    _cnt = 0
    for _cnt, item in enumerate(COMPILED.finditer(data)):
        print(f"\n{ALERT} : please don't use walrus operator")
        print(f"{file_}:\n{item.group()}\n")

    return _cnt
