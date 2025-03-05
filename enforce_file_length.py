MAX_FILE_LENGTH = 1000

EXCLUDE = {
}

ALERT = "BZG450"


def enforce_file_length(file_):
    if file_ in EXCLUDE:
        return 0

    with open(file_) as f:
        for _i, _ in enumerate(f):
            pass

    if _i > 1000:
        print(f"{ALERT}")
        print("{} file is too long: {} > {}".format(file_, _i, MAX_FILE_LENGTH))
        return 1

    return 0
