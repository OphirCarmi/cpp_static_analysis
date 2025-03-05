import sys
import time
import os
import os.path as osp
from enforce_file_length import enforce_file_length
from enforce_member_variables_naming_convention import (
    enforce_member_variables_naming_convention,
)
from enforce_static_function_naming_convention import (
    enforce_static_function_naming_convention,
)

from enforce_static_function_args_naming_convention import (
    enforce_static_function_args_naming_convention,
)
from enforce_global_function_args_naming_convention import (
    enforce_global_function_args_naming_convention,
)
from enforce_no_new_macros import enforce_no_new_macros

# from enforce_function_naming_convention import enforce_function_naming_convention
from enforce_for_variable_decl_naming_convention import (
    enforce_for_variable_decl_naming_convention,
)
from enforce_no_equal_bool_macros import enforce_no_equal_bool_macros
from enforce_no_else_after_return import enforce_no_else_after_return
from enforce_no_redundant_extern import enforce_no_redundant_extern
from enforce_type_format import enforce_type_format

from enforce_no_magic_numbers import enforce_no_magic_numbers
from enforce_no_simple_enum import enforce_no_simple_enum

# from enforce_no_div_by_zero import enforce_no_div_by_zero
from enforce_const_format import enforce_const_format
from enforce_no_copy_ctor import enforce_no_copy_ctor
from enforce_no_null import enforce_no_null

from enforce_file_name_format import enforce_file_name_format
from enforce_no_include_in_the_middle_of_file import (
    enforce_no_include_in_the_middle_of_file,
)
from enforce_no_attribute_in_h_file import enforce_no_attribute_in_h_file
from enforce_no_redundant_include import enforce_no_redundant_include
from enforce_no_empty_function import enforce_no_empty_function
from enforce_method_args_naming_convention import enforce_method_args_naming_convention
from enforce_enum_values_format import enforce_enum_values_format
from enforce_unused_fwd_decl import enforce_unused_fwd_decl
from enforce_single_statement_if import enforce_single_statement_if
from enforce_no_while import enforce_no_while
from enforce_no_boolean_trap import enforce_no_boolean_trap
from enforce_no_const_arithmetic_on_runtime import (
    enforce_no_const_arithmetic_on_runtime,
)
from enforce_no_typedef import enforce_no_typedef
from enforce_no_cv_mat_copy import enforce_no_cv_mat_copy
from enforce_no_walrus import enforce_no_walrus
from enforce_no_c_style import enforce_no_c_style
from get_user_literals import get_user_literals

from not_used.enforce_global_func_not_used import GLOBAL_FUNCS_FILE
from not_used.enforce_member_variable_not_used import MEMBER_VARS_FILE
from not_used.enforce_variable_not_used import VARS_FILE
from not_used.enforce_static_func_not_used import STATIC_FUNCS_FILE
from not_used.enforce_method_not_used import METHODS_FILE
from not_used.enforce_enum_vals_not_used import ENUM_VALS_FILE
from not_used.enforce_static_const_not_used import STATIC_CONST_FILE
from not_used.enforce_include_not_used import TYPE_FILE, USER_LITERALS_FILE
import not_used.main as not_used_main

subdirs = []

EXCLUDE_DIRS = {
    "/.venv/",
    "/tests/",
    "/3rdparty/",
    "/build/",
}

EXTENSIONS = {".cpp", ".h"}

INCLUDE = {}


def main_with_not_used(args):
    num_errors = 0
    for dir_ in subdirs:
        num_errors += process_one_dir(dir_, args)
        num_errors += not_used_main.process_one_dir(dir_)

    if num_errors:
        print("FAILURE, num errors: ", num_errors)
        sys.exit(-1)
    else:
        print("SUCCESS")
        sys.exit(0)


def main(args):
    num_errors = 0
    for dir_ in subdirs:
        num_errors += process_one_dir(dir_, args)

    if num_errors:
        print("FAILURE, num errors: ", num_errors)
        sys.exit(-1)
    else:
        print("SUCCESS")
        sys.exit(0)


def process_one_dir(dir_, args):
    time.sleep(0.5)
    for f in (
        METHODS_FILE,
        GLOBAL_FUNCS_FILE,
        STATIC_FUNCS_FILE,
        STATIC_CONST_FILE,
        MEMBER_VARS_FILE,
        VARS_FILE,
        ENUM_VALS_FILE,
        TYPE_FILE,
        USER_LITERALS_FILE,
    ):
        if osp.exists(f):
            os.remove(f)

    num_errors = 0
    if len(args) < 2:
        all_ = []
        for root, _, files in os.walk(dir_):
            for file_ in files:
                full_path = osp.join(root, file_)
                if any(x in full_path for x in EXCLUDE_DIRS):
                    continue

                if all(not full_path.endswith(x) for x in EXTENSIONS):
                    continue

                if INCLUDE and full_path not in INCLUDE:
                    continue

                all_.append(full_path)
    else:
        all_ = []
        for full_path in args:
            if any(x in full_path for x in EXCLUDE_DIRS):
                continue

            if all(not full_path.endswith(x) for x in EXTENSIONS):
                continue

            if INCLUDE and full_path not in INCLUDE:
                continue

            all_.append(full_path)

    for full_path in all_:
        num_errors += enforce_type_format(full_path)

    for full_path in all_:
        # print(full_path)
        num_errors += enforce_file_length(full_path)
        num_errors += enforce_method_args_naming_convention(full_path)
        num_errors += enforce_member_variables_naming_convention(full_path)
        num_errors += enforce_static_function_naming_convention(full_path)
        num_errors += enforce_static_function_args_naming_convention(full_path)
        num_errors += enforce_global_function_args_naming_convention(full_path)
        num_errors += enforce_no_new_macros(full_path)
        # num_errors += enforce_function_naming_convention(full_path)
        num_errors += enforce_for_variable_decl_naming_convention(full_path)
        num_errors += enforce_no_equal_bool_macros(full_path)
        num_errors += enforce_no_else_after_return(full_path)
        num_errors += enforce_no_redundant_extern(full_path)
        num_errors += enforce_no_magic_numbers(full_path)
        # num_errors += enforce_no_div_by_zero(full_path)
        num_errors += enforce_const_format(full_path)
        num_errors += enforce_no_copy_ctor(full_path)
        num_errors += enforce_no_include_in_the_middle_of_file(full_path)
        num_errors += enforce_no_attribute_in_h_file(full_path)
        num_errors += enforce_no_redundant_include(full_path)
        num_errors += enforce_no_empty_function(full_path)
        num_errors += enforce_enum_values_format(full_path)
        num_errors += enforce_no_simple_enum(full_path)
        num_errors += enforce_no_null(full_path)
        num_errors += enforce_file_name_format(full_path)
        num_errors += enforce_unused_fwd_decl(full_path)
        num_errors += enforce_single_statement_if(full_path)
        num_errors += enforce_no_while(full_path)
        num_errors += enforce_no_boolean_trap(full_path)
        num_errors += enforce_no_const_arithmetic_on_runtime(full_path)
        num_errors += enforce_no_typedef(full_path)
        num_errors += enforce_no_cv_mat_copy(full_path)
        num_errors += enforce_no_walrus(full_path)
        num_errors += enforce_no_c_style(full_path)
        get_user_literals(full_path)

    return num_errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        main_with_not_used(sys.argv)

    main(sys.argv)
