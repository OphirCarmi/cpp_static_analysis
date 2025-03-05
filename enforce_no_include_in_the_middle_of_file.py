from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG140"


def enforce_no_include_in_the_middle_of_file(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_, encoding="utf-8-sig") as f:
        data = f.read()

    data = comment_remover(data)

    in_the_middle = False
    for line in data.splitlines():
        line_wo_comment = line.strip("\n").strip(" ").strip()
        if line_wo_comment:
            if any(line_wo_comment.startswith(x) for x in ("#", "extern", "using")):
                if in_the_middle and any(
                    line_wo_comment.startswith(x) for x in ("#include", "using")
                ):
                    print(f"\n{ALERT} : include in the middle of the file")
                    print(f"{file_}\n{line}\n")
                    cnt += 1
                    break
            else:
                in_the_middle = True

    return cnt
