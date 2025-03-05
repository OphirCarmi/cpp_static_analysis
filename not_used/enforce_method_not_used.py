import os
import os.path as osp
import sys

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover  # noqa: E402

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG190"

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/3rdparty/",
    "/3rdparty/",
    "/build/",
}

EXTENSIONS = {".cpp", ".h"}

METHODS_FILE = "/tmp/methods.txt"


def enforce_method_not_used(dir_):
    if not osp.exists(METHODS_FILE):
        return 0

    methods = []
    with open(METHODS_FILE) as f:
        for line in f:
            vals = line.split(" ")
            methods.append((vals[0], vals[1].rstrip("\n")))

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
            for _f2, method in methods:
                if method in found:
                    continue

                if any(x + method in data for x in (".", "->")):
                    found.add(method)
                    continue

                for y in ("<", "("):
                    if any(x + method + y in data for x in (" ", "(", "!")):
                        found.add(method)
                        continue

                if any("::" + method + x in data for x in (")", " ")):
                    found.add(method)
                    continue

                if any(method + x in data for x in (",")):
                    found.add(method)
                    continue

                if "{" + method + "(" in data:
                    found.add(method)
                    continue

                if method + "::" + method in data:
                    found.add(method)
                    continue

    cnt = 0
    for file_, method in methods:
        if method not in found:
            if file_ in EXCLUDE:
                continue

            print(f"{ALERT}: Member method is not used")
            print(f'{file_}: "{method}" is not used\n')
            cnt += 1

    return cnt
