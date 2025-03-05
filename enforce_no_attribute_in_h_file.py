EXCLUDE = {
}

ALERT = "BZG440"


def enforce_no_attribute_in_h_file(file_):
    if not file_.endswith(".h"):
        return 0

    if file_ in EXCLUDE:
        return 0

    cnt = 0
    with open(file_) as f:
        for i, line in enumerate(f):
            if "__attribute__" in line:
                print(f"{ALERT}: Please don't use __attribute__ in header files")
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

    return cnt
