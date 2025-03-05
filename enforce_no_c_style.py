import re
from common import comment_remover

EXCLUDE_STRUCT = {
}

EXCLUDE_ENUM = {}

EXCLUDE_GOTO = {
}

EXCLUDE_INCLUDE = {
}

EXCLUDE_ASSIGN = {
}

INCLUDE = {}

ALERT_STRUCT = "BZG470"
ALERT_GOTO = "BZG471"
ALERT_INCLUDE = "BZG472"
ALERT_ASSIGN = "BZG473"
ALERT_ENUM = "BZG474"

COMPILED_STRUCT = re.compile(r"struct [A-Z][a-zA-Z0-9_]+ [^{:]")
COMPILED_ENUM = re.compile(r"enum [A-Z][a-zA-Z0-9_]+ [^{:]")
COMPILED_GOTO = re.compile(r"\bgoto\b")
COMPILED_ASSIGN_1 = re.compile(r"bool ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_2 = re.compile(r"int ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_3 = re.compile(r"float ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_4 = re.compile(r"double ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_5 = re.compile(r"int8_t ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_6 = re.compile(r"int16_t ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_7 = re.compile(r"int32_t ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_8 = re.compile(r"int64_t ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_9 = re.compile(r"size_t ([a-zA-Z0-9_]+) = ([^;)]+);")
COMPILED_ASSIGN_10 = re.compile(r"auto ([a-zA-Z0-9_]+) = ([^;)]+);")

COMPILED_ASSIGN = [
    COMPILED_ASSIGN_1,
    COMPILED_ASSIGN_2,
    COMPILED_ASSIGN_3,
    COMPILED_ASSIGN_4,
    COMPILED_ASSIGN_5,
    COMPILED_ASSIGN_6,
    COMPILED_ASSIGN_7,
    COMPILED_ASSIGN_8,
    COMPILED_ASSIGN_9,
    COMPILED_ASSIGN_10,
]


def enforce_no_c_style(file_):
    if INCLUDE and file_ not in INCLUDE:
        return 0

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data, remove_ifdef=False)

    cnt = 0
    for _cnt, item in enumerate(COMPILED_STRUCT.finditer(data)):
        if file_ in EXCLUDE_STRUCT:
            continue

        print(f'\n{ALERT_STRUCT} : c style, remove "struct"')
        print(f"{file_}:\n{item.group(0)}\n")
        cnt += 1

    for _cnt, item in enumerate(COMPILED_ENUM.finditer(data)):
        if file_ in EXCLUDE_ENUM:
            continue

        print(f'\n{ALERT_ENUM} : c style, remove "enum"')
        print(f"{file_}:\n{item.group(0)}\n")
        cnt += 1

    for _cnt, item in enumerate(COMPILED_GOTO.finditer(data)):
        if file_ in EXCLUDE_GOTO:
            continue

        print(f'\n{ALERT_GOTO} : c style, remove "goto"')
        print(f"{file_}:\n{item.group(0)}\n")
        cnt += 1

    for regex in COMPILED_ASSIGN:
        for _cnt, item in enumerate(regex.finditer(data)):
            if file_ in EXCLUDE_ASSIGN:
                continue

            print(f"\n{ALERT_ASSIGN} : c style, use {{}}")
            print(f"{file_}:\n{item.group(0)}\n")
            cnt += 1

    for line in data.splitlines():
        if file_ in EXCLUDE_INCLUDE:
            continue

        if ".h>" in line:
            print(f"\n{ALERT_INCLUDE} : c header, use c++")
            print(f"{file_}:\n{line}\n")
            cnt += 1

    return cnt
