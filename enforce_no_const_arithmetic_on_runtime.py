import re
from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG370"

COMPILED = [
    re.compile(r"k[A-Z][A-Za-z0-9_]+ \* k[A-Z][A-Za-z0-9_]+"),
    re.compile(r"k[A-Z][A-Za-z0-9_]+ \+ k[A-Z][A-Za-z0-9_]+"),
    re.compile(r"k[A-Z][A-Za-z0-9_]+ \- k[A-Z][A-Za-z0-9_]+"),
    re.compile(r"k[A-Z][A-Za-z0-9_]+ \/ k[A-Z][A-Za-z0-9_]+"),
    re.compile(r"k[A-Z][A-Za-z0-9_]+ \+ \d+"),
    re.compile(r"k[A-Z][A-Za-z0-9_]+ \- \d+"),
    re.compile(r"k[A-Z][A-Za-z0-9_]+ \* \d+"),
    re.compile(r"k[A-Z][A-Za-z0-9_]+ \/ \d+"),
    re.compile(r"[^A-za-z]\d+(\.\d+f)? \+ k[A-Z][A-Za-z0-9_]+"),
    re.compile(r"[^A-za-z]\d+(\.\d+f)? \- k[A-Z][A-Za-z0-9_]+"),
    re.compile(r"[^A-za-z]\d+(\.\d+f)? \* k[A-Z][A-Za-z0-9_]+"),
    re.compile(r"[^A-za-z]\d+(\.\d+f)? \/ k[A-Z][A-Za-z0-9_]+"),
]


def enforce_no_const_arithmetic_on_runtime(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    data = data.replace("\n", "")
    for it in COMPILED:
        for item in it.finditer(data):
            # print(item)
            start_ind = item.start(0)
            end_ind = item.end(0)
            for i in range(1000):
                if data[start_ind - i] == ";":
                    break

            line = data[start_ind - i + 1 : end_ind]
            # print(len(line))
            if not line or "constexpr" in line or "static const" in line:
                continue

            print(f"\n{ALERT} : Don't calc this on runtime")
            print(f"{file_}:\n{line}\n")
            cnt += 1

    return cnt
