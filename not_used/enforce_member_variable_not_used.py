import os
import os.path as osp
import sys

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover  # noqa: E402

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG180"

EXCLUDE_DIRS = {"/.venv/", "/tests/3rdparty/", "/3rdparty/", "/build/"}

EXTENSIONS = {".cpp", ".h"}

MEMBER_VARS_FILE = "/tmp/member_vars.txt"


def enforce_member_variable_not_used(dir_):
    if not osp.exists(MEMBER_VARS_FILE):
        return 0

    vars_ = []
    with open(MEMBER_VARS_FILE) as f:
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

                if any(x + var in data for x in (".", "->", "&")):
                    found.add(var)
                    continue

                if any(var + x in data for x in (")", " ", ",", ".", "->")):
                    found.add(var)
                    continue

    cnt = 0
    for file_, var in vars_:
        if var not in found:
            if file_ in EXCLUDE:
                continue

            if var.startswith("operator"):
                continue

            print(f"{ALERT}: Member var is not used")
            print(f'{file_}: "{var}" is not used\n')
            cnt += 1

    return cnt
