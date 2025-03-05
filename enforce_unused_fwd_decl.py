import re

from common import comment_remover, whole_word_count

EXCLUDE = {}

ALERT = "BZG290"

FWD_DECL = re.compile(r"(class|struct){1} ([A-Za-z0-9_]+);\n")


def enforce_unused_fwd_decl(file_):
    if file_ in EXCLUDE:
        return 0

    if not file_.endswith(".h"):
        return 0

    # print(file_)
    cnt = 0
    names = []
    with open(file_) as f:
        for i, line in enumerate(f):
            match = FWD_DECL.match(line)
            if match is not None:
                names.append((i, match.group(2)))

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    for i, name in names:
        if whole_word_count(name, data) < 2:
            print(f"{ALERT}: unused fwd decl")
            print(f"{file_}:{i + 1}\n {name}")
            cnt += 1

    return cnt
