import collections

EXCLUDE = {}

INCLUDE = {}

ALERT = "BZG270"


def enforce_no_duplicates_cmake(file_):
    if file_ in EXCLUDE:
        return 0

    if INCLUDE and file_ not in INCLUDE:
        return 0

    # print(file_)
    names = []
    with open(file_) as f:
        for line in f:
            line_s = line.strip("\n")
            if line_s.endswith(".cpp"):
                vals = line_s.split("/")
                if len(vals) < 3:
                    continue

                name = "/".join(vals[-2:])
                # print(name)
                names.append(name)

    duplicates = [
        item for item, count in collections.Counter(names).items() if count > 1
    ]
    # print(duplicates)
    _cnt = 0
    for _cnt, name in enumerate(duplicates, 1):
        print(f"\n{ALERT} : file name appears twice")
        print(f'{file_}:\n "{name}" appears twice\n')

    return _cnt
