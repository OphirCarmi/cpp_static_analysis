EXCLUDE_ENDIF = {
}

EXCLUDE_ELSE = {
}

EXCLUDE_NEW_MACRO = {
}

ALERT_NEW_MACRO = "BZG030"
ALERT_ELSE = "BZG031"
ALERT_ENDIF = "BZG032"

SUBDIR = ""


def enforce_no_new_macros(file_):
    cnt = 0
    with open(file_) as f:
        for i, line in enumerate(f):
            if not i:
                last_line = line
                continue

            if f"suppress {ALERT_NEW_MACRO}" in last_line:
                last_line = line
                continue

            if file_ not in EXCLUDE_NEW_MACRO and line.startswith("#define "):
                v = line.split(" ")[1]
                if not v.startswith(SUBDIR):
                    print(f"{ALERT_NEW_MACRO}: Please don't add new macros, use c++")
                    print(f"{file_}:{str(i)} {line}")
                    cnt += 1

            line_s = line.strip(" ")
            if file_ not in EXCLUDE_ELSE and line_s == "#else\n":
                print(f"{ALERT_ELSE}: Please add comment")
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

            if file_ not in EXCLUDE_ENDIF and line_s == "#endif\n":
                print(f"{ALERT_ENDIF}: Please add comment")
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

            last_line = line

    return cnt
