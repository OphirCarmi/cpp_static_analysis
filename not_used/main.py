import sys
from .enforce_method_not_used import enforce_method_not_used
from .enforce_global_func_not_used import enforce_global_func_not_used
from .enforce_static_func_not_used import enforce_static_func_not_used
from .enforce_member_variable_not_used import enforce_member_variable_not_used
from .enforce_variable_not_used import enforce_variable_not_used
from .enforce_enum_vals_not_used import enforce_enum_vals_not_used
from .enforce_include_not_used import enforce_include_not_used
from .enforce_variable_not_used_immediately import enforce_variable_not_used_immediately
from .enforce_static_const_not_used import enforce_static_const_not_used
from .enforce_inline_functions import enforce_inline_functions

SUBDIRS = []


def main():
    num_errors = 0
    for dir_ in SUBDIRS:
        num_errors += process_one_dir(dir_)

    if num_errors:
        print("FAILURE, num errors: ", num_errors)
        sys.exit(-1)
    else:
        print("SUCCESS")
        sys.exit(0)


def process_one_dir(dir_):
    num_errors = 0
    num_errors += enforce_method_not_used(dir_)
    num_errors += enforce_global_func_not_used(dir_)
    num_errors += enforce_static_func_not_used(dir_)
    num_errors += enforce_member_variable_not_used(dir_)
    num_errors += enforce_variable_not_used(dir_)
    num_errors += enforce_enum_vals_not_used(dir_)
    num_errors += enforce_static_const_not_used(dir_)
    num_errors += enforce_include_not_used(dir_)
    num_errors += enforce_variable_not_used_immediately(dir_)
    num_errors += enforce_inline_functions(dir_)

    return num_errors


if __name__ == "__main__":
    main()
