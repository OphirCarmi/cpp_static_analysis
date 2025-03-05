import re

from common import comment_remover, get_bracket_section

EXCLUDE = {
}

INCLUDE = {}

ALERT_IF = "BZG300"
ALERT_FOR = "BZG301"
ALERT_IF_INSIDE_IF = "BZG302"

SINGLE_STATEMENT_IF = re.compile(r"\n[ ]+if \([^{;]+\{[ \n]+[^;]+;\n\s+\}\n")
SINGLE_STATEMENT_FOR = re.compile(r"\n[ ]+for \([^{]+\{\n[^;]+;\n\s+\}\n")


def enforce_single_statement_if(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)

    for item in SINGLE_STATEMENT_IF.findall(data):
        if "LOG" in item:
            continue

        print(f"\n{ALERT_IF} : no need for curly brackets in a single statement if")
        print(f'{file_}:\n"{item}"\n')
        cnt += 1

    for item in SINGLE_STATEMENT_FOR.findall(data):
        if "LOG" in item:
            continue

        print(f"\n{ALERT_FOR} : no need for curly brackets in a single statement for")
        print(f'{file_}:\n"{item}"\n')
        cnt += 1

    curr = 0
    while True:
        curr = data.find("if (", curr + 1)
        if curr < 0:
            break

        brackets_indices = get_bracket_section(data, curr, "()")
        semicolon_ind = data.find(";", curr + 1)
        opening_bracket_ind = data.find("{", curr + 1)
        if 0 < semicolon_ind < opening_bracket_ind:
            continue

        brackets_indices = get_bracket_section(data, curr, "{}")
        if brackets_indices[0] is None:
            continue

        if_body = data[brackets_indices[0] : brackets_indices[1]]
        second_if = if_body.find("if (")
        if second_if < 0:
            continue

        semicolon_ind = if_body.find(";")
        if 0 < semicolon_ind < second_if:
            continue

        opening_bracket_ind = if_body.find("}")
        if opening_bracket_ind < 0:
            continue

        semicolon_ind = if_body.find(";", opening_bracket_ind)
        if 0 < semicolon_ind:
            continue

        else_ind = data.find("else", brackets_indices[1])
        semicolon_ind = data.find(";", brackets_indices[1])
        third_if_ind = data.find("if", brackets_indices[1])
        if 0 < third_if_ind < else_ind:
            print(f"\n{ALERT_IF_INSIDE_IF} : no need for two if's")
            print(f'{file_}:\n"{if_body}"\n')
            cnt += 1

        if 0 < semicolon_ind < else_ind:
            continue

        if else_ind >= 0:
            continue

        print(f"\n{ALERT_IF_INSIDE_IF} : no need for two if's")
        print(f'{file_}:\n"{if_body}"\n')
        cnt += 1

    return cnt
