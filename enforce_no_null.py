from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG250"


def enforce_no_null(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    if "NULL" in data:
        ind = data.index("NULL")
        line = data[ind : data.index("\n", ind)]
        print(f"\n{ALERT} : Don't use NULL, use nullptr")
        print(f"{file_}:\n{line}\n")
        cnt += 1

    return cnt
