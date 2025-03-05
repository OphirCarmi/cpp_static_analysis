import os
import os.path as osp
import sys

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover  # noqa: E402

EXCLUDE = {
}

SUPPRESS = {
}

INCLUDE = {}

ALERT = "BZG400"

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/3rdparty/",
    "/3rdparty/",
    "/build/",
    "/nadav_watch/",
    "/speaker/",
    "tests/",
}

EXTENSIONS = {".cpp", ".h"}

VARS_FILE = "/tmp/vars.txt"


def enforce_variable_not_used_immediately(dir_):
    if not osp.exists(VARS_FILE):
        return 0

    vars_ = []
    with open(VARS_FILE) as f:
        for line in f:
            vals = line.split(" ")
            vars_.append((vals[0], vals[1].rstrip("\n")))

    cnt = 0
    for root, _, files in os.walk(dir_):
        for file_ in files:
            if file_.endswith(".h"):
                continue

            full_path = osp.join(root, file_)
            if INCLUDE and full_path not in INCLUDE:
                continue

            if full_path in EXCLUDE:
                continue

            if any(x in full_path for x in EXCLUDE_DIRS):
                continue

            if all(not full_path.endswith(x) for x in EXTENSIONS):
                continue

            # print(full_path)
            with open(full_path) as f:
                data = f.read()

            data = comment_remover(data)
            for _, var in vars_:
                if var.startswith("k"):
                    continue

                pattern = " " + var + "{"
                if pattern not in data:
                    continue

                decl_ind = data.find(pattern)
                if data[decl_ind - 1] == " ":
                    continue

                usage_ind = data.find(var, decl_ind + 2)
                found = True
                if usage_ind < 0:
                    usage_ind = data.find("&" + var, decl_ind + 2)
                    if usage_ind < 0:
                        found = False

                distance = data.count("\n", decl_ind, usage_ind)
                th = SUPPRESS.get(full_path, 7)
                if not found or distance > th:
                    print(f"{ALERT}: var is not used immediately")
                    print(
                        f'{full_path}:\n "{var}" distance from declaration is {distance} rows\n',
                    )
                    cnt += 1

    return cnt
