from common import comment_remover, is_camel_case

from not_used.enforce_include_not_used import TYPE_FILE

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG330"


def enforce_type_format(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    with open(file_) as f:
        for i, line in enumerate(f):
            line = comment_remover(line)
            if not any(
                line.startswith(x) for x in ("enum ", "struct ", "class ", "using ")
            ):
                continue

            if not line.endswith("{\n") and not all(
                x in line for x in ("using ", " = ")
            ):
                continue

            if "*" in line:
                continue

            if "enum class " in line:
                name = line.split("enum class ")[1].split(" ")[0]

            elif "enum " in line:
                name = line.split("enum ")[1].split(" ")[0]

            elif "struct " in line:
                name = line.split("struct ")[1].split(" ")[0]

            elif "class " in line:
                name = line.split("class ")[1].split(" ")[0]

            elif line.startswith("using ") and " = " in line:
                name = line.strip("\n").split(" ")[1]
                if name == "json":
                    continue

            with open(TYPE_FILE, "a") as f:
                f.write(file_ + " " + name + "\n")

            if not is_camel_case(name) or name[0].islower():
                print(f"\n{ALERT} : type name should be CamelCase")
                print(f'{file_}:{i}\n{line}\n"{name}" name is not CamelCase\n')
                cnt += 1

    return cnt
