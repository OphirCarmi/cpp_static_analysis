from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG320"

WHILE = "while ("


def enforce_no_while(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)

    if WHILE in data:
        ind = data.index(WHILE)
        line = data[ind : data.index("\n", ind)]
        print(f"\n{ALERT} : don't use while, use for instead")
        print(f'{file_}:\n "{line}"\n')
        cnt += 1

    return cnt
