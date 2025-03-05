import re

from common import comment_remover

EXCLUDE = {}

ALERT = "BZG390"


COMPILED = re.compile(r" cv::Mat [a-zA-Z0-9_]+ = [a-zA-Z0-9_\->.]+\(")


def enforce_no_cv_mat_copy(file_):
    if file_ in EXCLUDE:
        return 0

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    _cnt = 0
    for _cnt, item in enumerate(COMPILED.finditer(data)):
        print(f'{ALERT}: Please don\'t copy mats (=), use "auto" or ctor with rect')
        print(f"{file_}:\n{item.group()}\n")

    return _cnt
