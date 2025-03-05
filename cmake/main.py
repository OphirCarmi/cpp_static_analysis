import sys
import os
import os.path as osp

from enforce_no_duplicates_cmake import enforce_no_duplicates_cmake


THIS_DIR = osp.dirname(__file__)

SUBDIR = ""

dir_ = osp.join(THIS_DIR, "..", "..", SUBDIR)

EXCLUDE = {"/.venv/", "/3rdparty/", "/build/"}

EXTENSIONS = {"CMakeLists.txt"}


def main():
    num_errors = 0
    for root, _, files in os.walk(dir_):
        for file_ in files:
            full_path = osp.join(root, file_)
            if any(x in full_path for x in EXCLUDE):
                continue

            if all(not full_path.endswith(x) for x in EXTENSIONS):
                continue

            # print(full_path)
            num_errors += enforce_no_duplicates_cmake(full_path)

    if num_errors:
        print("FAILURE, num errors: ", num_errors)
        sys.exit(-1)

    else:
        print("SUCCESS")
        sys.exit(0)


if __name__ == "__main__":
    main()
