import os.path as osp

EXCLUDE = {}

INCLUDE = {}

ALERT = "BZG260"


def enforce_file_name_format(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    name = osp.basename(file_)
    if name.lower() != name:
        print(f"\n{ALERT} : file name should be snake_case")
        print(f'{file_}: "{name}" is not snake case\n')
        cnt += 1

    return cnt
