from common import get_all_static_func_indices, is_camel_case
from not_used.enforce_static_func_not_used import STATIC_FUNCS_FILE

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG010"


def enforce_static_function_naming_convention(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    # print(file_)
    if file_.endswith(".h"):
        return cnt

    with open(file_) as f:
        data = f.read()

    start_ind = 0
    func_indices = get_all_static_func_indices(data, start_ind)
    for func_ind in func_indices:
        func_decl_line = data[func_ind : data.find("\n", func_ind + 1)]
        func_name = func_decl_line.split("(")[0].split(" ")[-1].strip("*&")
        if "{" in func_name:
            continue

        with open(STATIC_FUNCS_FILE, "a") as f:
            f.write(file_ + " " + func_name + "\n")

        if not is_camel_case(func_name) or func_name[0].islower():
            if func_decl_line.strip("\n ").startswith("static const"):
                continue

            cnt += 1
            with open(file_) as f:
                for i, line in enumerate(f):
                    if line.strip("\n") == func_decl_line[1:]:
                        print(f"\n{ALERT} : function name should be snake_case")
                        print(
                            f'{file_}:{str(i)}\n{line}\n "{func_name}" func name is not CamelCase\n',
                        )

    return cnt
