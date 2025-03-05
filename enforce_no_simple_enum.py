from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG240"


def enforce_no_simple_enum(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    if "enum " in data and "enum class" not in data:
        ind = data.index("enum ")
        line = data[ind : data.index("\n", ind)]
        print(f"\n{ALERT} : Don't use simple enum, use enum class instead")
        print(f"{file_}:\n{line}\n")
        cnt += 1

    return cnt
