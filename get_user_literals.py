import re

from not_used.enforce_include_not_used import USER_LITERALS_FILE

COMPLIED = re.compile(r"operator\"\"(_[^ (]+)")


def get_user_literals(file_):
    with open(file_) as f:
        for line in f:
            match = COMPLIED.search(line)
            if match is not None:
                with open(USER_LITERALS_FILE, "a") as f:
                    f.write(file_ + " " + match.group(1) + "\n")
