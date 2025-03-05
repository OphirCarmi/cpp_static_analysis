import os
import os.path as osp
import sys
from collections import defaultdict

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover  # noqa: E402

EXCLUDE = {}

INCLUDE = {}

ALERT = "BZG230"

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/3rdparty/",
    "/3rdparty/",
    "/build/",
}

INCLUDE_DIRS = {}

EXTENSIONS = {".cpp", ".h"}

GLOBAL_FUNCS_FILE = "/tmp/global_funcs.txt"


def enforce_global_func_not_used(dir_):
    if not osp.exists(GLOBAL_FUNCS_FILE):
        print(
            "{} doesn't exist, run static_analysis before this one".format(
                GLOBAL_FUNCS_FILE,
            ),
        )
        return 0

    funcs = []
    with open(GLOBAL_FUNCS_FILE) as f:
        for line in f:
            vals = line.split(" ")
            funcs.append((vals[0], vals[1].rstrip("\n")))

    files_of_funcs = defaultdict(set)
    for file_, func in funcs:
        files_of_funcs[func].add(file_)

    first = defaultdict(set)
    for root, _, files in os.walk(dir_):
        for file_ in files:
            full_path = osp.join(root, file_)
            if INCLUDE_DIRS and not any(x in full_path for x in INCLUDE_DIRS):
                continue

            if any(x in full_path for x in EXCLUDE_DIRS):
                continue

            if all(not full_path.endswith(x) for x in EXTENSIONS):
                continue

            # print(full_path)
            with open(full_path) as f:
                data = f.read()

            data = comment_remover(data)
            for _, func in funcs:
                for y in ("<", "(", ","):
                    for x in (" ", "(", "!", "*"):
                        ind = 0
                        while True:
                            ind = data.find(x + func + y, ind + 1)
                            if ind < 0:
                                break

                            first[func].add(ind)

    c = {func: len(s) for func, s in first.items()}

    cnt = 0
    for file_, func in funcs:
        if func not in c:
            if file_ in EXCLUDE:
                continue

            if INCLUDE_DIRS and not any(x in file_ for x in INCLUDE_DIRS):
                continue

            th = 3
            if len(files_of_funcs[func]) == 1 and next(
                iter(files_of_funcs[func]),
            ).endswith(".h"):
                th = 2

            if c[func] >= th:
                continue

            if func in c:
                print(func, c[func])

            print(f"{ALERT}: global func is not used")
            print(f'{file_}: "{func}" is not used\n')
            cnt += 1

    return cnt
