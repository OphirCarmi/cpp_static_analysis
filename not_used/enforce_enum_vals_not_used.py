import os
import os.path as osp
import sys

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover  # noqa: E402

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG340"

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/3rdparty/",
    "/3rdparty/",
    "/build/",
}

EXTENSIONS = {".cpp", ".h"}

ENUM_VALS_FILE = "/tmp/enum_vals.txt"


def enforce_enum_vals_not_used(dir_):
    if not osp.exists(ENUM_VALS_FILE):
        print(
            "{} doesn't exist, run static_analysis before this one".format(
                ENUM_VALS_FILE,
            ),
        )
        return 0

    enum_vals = []
    with open(ENUM_VALS_FILE) as f:
        for line in f:
            vals = line.split(" ")
            enum_vals.append((vals[0], vals[1].rstrip("\n")))

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
            for _, enum_val in enum_vals:
                if enum_val in found:
                    continue

                if enum_val in data:
                    found.add(enum_val)
                    continue

    cnt = 0
    for file_, enum_val in enum_vals:
        if enum_val not in found:
            if file_ in EXCLUDE:
                continue

            print(f"{ALERT}: func is not used")
            print(f'{file_}: "{enum_val}" is not used\n')
            cnt += 1

    return cnt
