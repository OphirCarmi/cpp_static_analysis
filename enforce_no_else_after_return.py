import re

EXCLUDE = {}

INCLUDE = {}

ALERT_RETURN = "BZG080"
ALERT_CONTINUE = "BZG081"
ALERT_BREAK = "BZG082"

COMPILED_RETURN = re.compile(r"[\t ]+return[^;]*;")
COMPILED_ELSE = re.compile(r"[\t ]+} else ")
COMPILED_CONTINUE = re.compile(r"[\t ]+continue;")
COMPILED_BREAK = re.compile(r"[\t ]+break;")


def enforce_no_else_after_return(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    last_line = ""
    with open(file_) as f:
        for i, line in enumerate(f):
            if not last_line or not COMPILED_ELSE.search(line.strip("\n")):
                last_line = line
                continue

            if COMPILED_RETURN.match(last_line.strip("\n")):
                print(f"{ALERT_RETURN}: no need of else after return")
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

            if COMPILED_CONTINUE.match(last_line.strip("\n")):
                print(f"{ALERT_CONTINUE}: no need of else after continue")
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

            if COMPILED_BREAK.match(last_line.strip("\n")):
                print(f"{ALERT_BREAK}: no need of else after break")
                print(f"{file_}:{str(i)} {line}")
                cnt += 1

            last_line = line

    return cnt
