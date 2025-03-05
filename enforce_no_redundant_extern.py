from common import comment_remover, whole_word_count

EXCLUDE = {}

INCLUDE = {}

ALERT = "BZG090"


def enforce_no_redundant_extern(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    names = []
    with open(file_) as f:
        for i, line in enumerate(f):
            line_wo_comment = comment_remover(line)
            if line_wo_comment.startswith("extern "):
                name = line_wo_comment.split(" ")[-1].strip(";\n[]{")
                if not name:
                    continue

                if name.startswith("k") and name[1].isupper():
                    continue

                names.append((i, line, name))

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    for i, line, name in names:
        if whole_word_count(name, data) < 2:
            print(f"\n{ALERT} : reduandant extern")
            print(f'{file_}:{str(i + 1)}\n{line}\n "{name}" is not used\n')
            cnt += 1

    return cnt
