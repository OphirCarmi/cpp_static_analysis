from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG160"


def enforce_no_empty_function(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    for line in data.splitlines():
        if "() {}" in line and "virtual" not in line and "constexpr" not in line:
            print(f"\n{ALERT} : found empty function")
            print(f"{file_}\n{line}\n found empty function\n")
            cnt += 1

    return cnt
