import os
import os.path as osp
import sys
from collections import defaultdict

sys.path.append(osp.dirname(osp.dirname(__file__)))

from not_used.enforce_global_func_not_used import GLOBAL_FUNCS_FILE  # noqa: E402
from not_used.enforce_member_variable_not_used import MEMBER_VARS_FILE  # noqa: E402
from not_used.enforce_method_not_used import METHODS_FILE  # noqa: E402
from not_used.enforce_enum_vals_not_used import ENUM_VALS_FILE  # noqa: E402
from not_used.enforce_static_const_not_used import STATIC_CONST_FILE  # noqa: E402

from common import comment_remover  # noqa: E402


EXCLUDE = {
}

INCLUDE = {}

ALERT_NOT_USED = "BZG350"
ALERT_DUPLICATE = "BZG351"

EXCLUDE_DIRS = {"/.venv/", "/tests/", "/tests/3rdparty/", "/3rdparty/", "/build/"}

EXTENSIONS = {".cpp", ".h"}

TYPE_FILE = "/tmp/types.txt"
USER_LITERALS_FILE = "/tmp/user_literals.txt"

SUBDIR = ""


def enforce_include_not_used(dir_):
    vals = defaultdict(set)
    for file_ in (
        ENUM_VALS_FILE,
        GLOBAL_FUNCS_FILE,
        MEMBER_VARS_FILE,
        METHODS_FILE,
        STATIC_CONST_FILE,
        TYPE_FILE,
        USER_LITERALS_FILE,
    ):
        if not osp.exists(file_):
            print("{} doesn't exist, run static_analysis before this one".format(file_))
            return 0

        with open(file_) as f:
            for line in f:
                filename, val = line.rstrip("\n").split(" ")
                vals[filename].add(val)

    # collect includes from all files
    includes = defaultdict(set)
    for root, _, files in os.walk(dir_):
        for file_ in files:
            full_path = osp.join(root, file_)
            if any(x in full_path for x in EXCLUDE_DIRS):
                continue

            if all(not full_path.endswith(x) for x in EXTENSIONS):
                continue

            with open(full_path) as f:
                for line in f:
                    if line.startswith('#include "'):
                        include = line.rstrip("\n").split(" ")[1].strip('"')
                        if include.startswith("3rdparty/"):
                            continue

                        include = SUBDIR + "/" + include
                        if (
                            include.endswith("include.h")
                            or include.endswith("includes.h")
                            or include in EXCLUDE
                        ):
                            continue

                        includes[full_path].add(include)

    cnt = 0
    for file_, file_includes in includes.items():
        with open(file_) as f:
            data = f.read()

        data = comment_remover(data)
        for f_inc in file_includes:
            for v in vals[f_inc]:
                if v in data:
                    break
            else:
                if (
                    file_.endswith("include.h")
                    or file_.endswith("includes.h")
                    or file_ in EXCLUDE
                    or file_.replace(".cpp", ".h") == f_inc
                ):
                    continue

                print(f"{ALERT_NOT_USED}: include is not used")
                print(f'{file_}: "{f_inc}" is not used\n')
                cnt += 1

            if file_.endswith(".h"):
                cpp = file_.replace(".h", ".cpp")
                if cpp in includes and f_inc in includes[cpp]:
                    print(f"{ALERT_DUPLICATE}: include is in cpp and header")
                    print(f'{file_}: "{f_inc}" remove one of them\n')
                    cnt += 1

    return cnt
