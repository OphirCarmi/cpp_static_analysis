import os
import os.path as osp
import sys

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover, whole_word_count  # noqa: E402

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG310"

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/3rdparty/",
    "/3rdparty/",
    "/build/",
}

EXTENSIONS = {".cpp", ".h"}

VARS_FILE = "/tmp/vars.txt"


def enforce_variable_not_used(dir_):
    if not osp.exists(VARS_FILE):
        return 0

    vars_ = []
    with open(VARS_FILE) as f:
        for line in f:
            vals = line.split(" ")
            vars_.append((vals[0], vals[1].rstrip("\n")))

    found = set()
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
            for _, var in vars_:
                if var in found:
                    continue

                cnt = whole_word_count(var, data)
                equal_cnt = data.count(" " + var + " = ")
                equal_cnt += data.count(" " + var + " =\n")
                equal_cnt += data.count(" " + var + "(")
                equal_cnt += data.count(" " + var + "{")
                if cnt - equal_cnt > 0:
                    found.add(var)

    cnt = 0
    for file_, var in vars_:
        if var.startswith("++") or var.endswith("++"):
            continue

        if any(var.startswith(x) for x in "!'-"):
            continue

        var = var.strip("{}<>!|)")
        if not var:
            continue

        if var.startswith("static_cast"):
            continue

        if var.startswith("LOG"):
            continue

        if var == "free":
            continue

        if var not in found:
            if file_ in EXCLUDE:
                continue

            print(f"{ALERT}: var is not used")
            print(f'{file_}: "{var}" is not used\n')
            cnt += 1

    return cnt
