EXCLUDE = {
}

ALERT_EQUALS_BOOL = "BZG070"


def enforce_no_equal_bool_macros(file_):
    if file_ in EXCLUDE:
        return 0

    cnt = 0
    with open(file_) as f:
        for i, line in enumerate(f):
            if not i:
                last_line = line
                continue

            if f"suppress {ALERT_EQUALS_BOOL}" in last_line:
                last_line = line
                continue

            if line.startswith("#"):
                continue

            if any(x in line for x in ("== true", "true ==")):
                print(f'{ALERT_EQUALS_BOOL}: Please remove "== true" or "true =="')
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

            if any(x in line for x in ("== false", "false ==")):
                print(
                    f'{ALERT_EQUALS_BOOL}: Please remove "== false" or "false ==" and use "!" instead',
                )
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

            last_line = line

    return cnt
