EXCLUDE = {
}

ALERT = "BZG380"


def enforce_no_typedef(file_):
    if file_ in EXCLUDE:
        return 0

    cnt = 0
    with open(file_) as f:
        for i, line in enumerate(f):
            if line.startswith("typedef "):
                print(f'{ALERT}: Please don\'t use typedef, use "using" instead')
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

    return cnt
