from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG150"

PATTERNS = {
    (
        "#include <execution>",
        (
            "std::execution::par",
            "std::execution::par_unseq",
        ),
    ),
    ("#include <vector>", ("std::vector",)),
    (
        "#include <string>",
        (
            "std::string ",
            "std::string>",
            "std::string*",
            "std::string&",
            "std::string(",
            "std::to_string",
        ),
    ),
    ('using std::string_literals::operator""s;', ('"s ',)),
    ("using json = nlohmann::json;", ("json",)),
    ("#include <string_view>", ("std::string_view",)),
    ("#include <array>", ("std::array",)),
    ("#include <list>", ("std::list",)),
    ("#include <chrono>", ("std::chrono",)),
    (
        "#include <thread>",
        (
            "std::thread",
            "std::this_thread",
        ),
    ),
    ("#include <map>", ("std::map",)),
    ("#include <tuple>", ("std::tuple",)),
    ("#include <utility>", ("std::pair", "std::make_pair")),
    ("#include <unordered_map>", ("std::unordered_map",)),
    ("#include <mutex>", ("std::mutex",)),
    ("#include <limits>", ("std::numeric_limits",)),
    ("#include <fstream>", ("fstream",)),
    ("#include <ostream>", ("ostream",)),
    ("#include <atomic>", ("std::atomic",)),
    ("#include <iostream>", ("std::cout",)),
    ('#include "Opencv-Static/json_include.h"', ("using json",)),
    ("#include <sstream>", ("stringstream",)),
    (
        "#include <cstddef>",
        (
            "size_t",
            "int64_t",
            "uint16_t",
        ),
    ),
    ("#include <math.h>", ("sqrt",)),
    (
        "#include <memory>",
        (
            "std::shared_ptr",
            "std::unique_ptr",
            "std::make_unique",
            "std::make_shared",
        ),
    ),
    ('#include "log/plog_include.h"', ("LOG",)),
    ('#include "Opencv-Static/opencv_includes.h"', ("cv::",)),
    ("#include <dirent.h>", ("DIR",)),
    ("#include <string.h>", ("memset", "sprintf", "strtol", "strlen")),
    (
        "#include <stdint.h>",
        (
            "uint8_t",
            "uint16_t",
            "uint32_t",
            "int64_t",
            "int8_t",
            "int16_t",
            "int32_t",
            "int64_t",
        ),
    ),
    ("#include <iomanip>", ("std::hex", "std::right", "std::setw", "std::setfill")),
    (
        "#include <algorithm>",
        (
            "std::transform",
            "std::min",
            "std::max",
            "std::sort",
            "std::remove",
            "std::count_if",
            "std::find_if",
            "std::any_of",
            "std::generate",
        ),
    ),
    ("#include <condition_variable>", ("std::condition_variable",)),
    ("#include <climits>", ("CHAR_BIT", "INT_MAX")),
    ("#include <signal.h>", ("aaa",)),
    ("#include <sys/stat.h>", ("S_IRWXU", "stat")),
    ("#include <sys/statvfs.h>", ("statvfs",)),
    ("#include <sys/prctl.h>", ("PR_",)),
    ("#include <linux/input-event-codes.h>", ("EV_KEY", "KEY_DOWN")),
    ("#include <fcntl.h>", ("O_RDONLY", "O_WRONLY", "fcntl", "O_RDWR")),
    ("#include <unistd.h>", ("read", "usleep", "sleep", "sysconf", "close", "write")),
}


def enforce_no_redundant_include(file_):
    if file_ in EXCLUDE:
        return 0

    if INCLUDE and file_ not in INCLUDE:
        return 0

    # print(file_)
    cnt = 0
    for include, pattern in PATTERNS:
        cnt += check_one_type(file_, include, pattern)

    return cnt


def check_one_type(file_, include, pattern):
    with open(file_, encoding="utf-8-sig") as f:
        include_line_ind = -1
        for i, line in enumerate(f):
            line = comment_remover(line)
            if line.strip("\n") == include:
                include_line_ind = i
                continue

            if include_line_ind > 0 and any(x in line for x in pattern):
                return 0

    if include_line_ind < 0:
        return 0

    print(f"\n{ALERT} : include is not being used")
    print(f'{file_}:{str(include_line_ind + 1)}\n"{include}" is not used\n')
    return 1
