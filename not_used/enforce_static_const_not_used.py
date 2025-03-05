import os
import os.path as osp
import sys
from collections import Counter

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover, whole_word_count  # noqa: E402

EXCLUDE = {}

INCLUDE = {}

ALERT = "BZG280"

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/3rdparty/",
    "/3rdparty/",
    "/build/",
}

EXTENSIONS = {".cpp", ".h"}

STATIC_CONST_FILE = "/tmp/static_const.txt"


def enforce_static_const_not_used(dir_):
    if not osp.exists(STATIC_CONST_FILE):
        print(
            "{} doesn't exist, run static_analysis before this one".format(
                STATIC_CONST_FILE,
            ),
        )
        return 0

    consts = []
    with open(STATIC_CONST_FILE) as f:
        for line in f:
            vals = line.split(" ")
            consts.append((vals[0], vals[1].rstrip("\n")))

    found = []
    for root, _, files in os.walk(dir_):
        for file_ in files:
            full_path = osp.join(root, file_)
            if any(x in full_path for x in EXCLUDE_DIRS):
                continue

            if all(not full_path.endswith(x) for x in EXTENSIONS):
                continue

            # print(full_path)
            with open(full_path) as f:
                data = f.read()

            data = comment_remover(data)
            for _, const in consts:
                for _ in range(whole_word_count(const, data)):
                    # TODO(oc): check cpp and h files differently
                    found.append(const)

    c = Counter(found)
    cnt = 0
    for file_, const in consts:
        if const not in c or c[const] == 1:
            if file_ in EXCLUDE:
                continue

            print(f"{ALERT}: static const is not used")
            print(f'{file_}: "{const}" is not used\n')
            cnt += 1

    return cnt
