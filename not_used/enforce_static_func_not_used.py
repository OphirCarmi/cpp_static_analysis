import os
import os.path as osp
import sys
from collections import Counter

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover  # noqa: E402

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG170"

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/3rdparty/",
    "/3rdparty/",
    "/build/",
}

EXTENSIONS = {".cpp", ".h"}

STATIC_FUNCS_FILE = "/tmp/static_funcs.txt"


def enforce_static_func_not_used(dir_):
    if not osp.exists(STATIC_FUNCS_FILE):
        print(
            "{} doesn't exist, run static_analysis before this one".format(
                STATIC_FUNCS_FILE,
            ),
        )
        return 0

    funcs = []
    with open(STATIC_FUNCS_FILE) as f:
        for line in f:
            vals = line.split(" ")
            funcs.append((vals[0], vals[1].rstrip("\n")))

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
            for _, func in funcs:
                for x in ("(", "<"):
                    if func + x in data:
                        for _ in range(data.count(func + x)):
                            found.append(func)

                if func + "," in data:
                    found.append(func)

    c = Counter(found)
    cnt = 0
    for file_, func in funcs:
        if func not in c or c[func] == 1:
            if file_ in EXCLUDE:
                continue

            print(f"{ALERT}: func is not used")
            print(f'{file_}: "{func}" is not used\n')
            cnt += 1

    return cnt
