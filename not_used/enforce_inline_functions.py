import os
import os.path as osp
import sys
from .enforce_global_func_not_used import GLOBAL_FUNCS_FILE

sys.path.append(osp.dirname(osp.dirname(__file__)))

from common import comment_remover, get_bracket_section  # noqa: E402

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG420"

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/3rdparty/",
    "/3rdparty/",
    "/build/",
}

INCLUDE_DIRS = {}

EXTENSIONS = {".cpp", ".h"}


def enforce_inline_functions(dir_):
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

    cnt = 0
    for root, _, files in os.walk(dir_):
        for file_ in files:
            full_path = osp.join(root, file_)
            if full_path in EXCLUDE:
                continue

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
                for y in ("<", "("):
                    ind = 0
                    while True:
                        ind = data.find(" " + func + y, ind + 1)
                        if ind < 0:
                            break

                        bracket_ind = data.find("{", ind)
                        semicolon_ind = data.find(";", ind)
                        if 0 < semicolon_ind < bracket_ind:
                            ind = semicolon_ind
                            continue

                        indices = get_bracket_section(data, ind, "()")
                        bracket_ind = data.find("{", indices[1])
                        semicolon_ind = data.find(";", indices[1])
                        if 0 < semicolon_ind < bracket_ind:
                            ind = semicolon_ind
                            continue

                        curly_indices = get_bracket_section(data, indices[1], "{}")

                        if data.count("\n", curly_indices[0], curly_indices[1]) < 2:
                            for i in range(1000):
                                if data[ind - i] == "\n":
                                    break

                            start = ind - i
                            end = data.find("\n", ind)
                            line = data[start + 1 : end]
                            if line.startswith("inline"):
                                continue

                            print(f"{ALERT}: consider using inline func")
                            print(f'{full_path}: "{func}" should be inline\n')
                            cnt += 1

    return cnt
