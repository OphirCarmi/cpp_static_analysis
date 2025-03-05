import re

EXCLUDE = {}

ALERT = "BZG130"

CLASSES = {"cv::Mat", "cv::Rect", "std::string", "cv::Point", "cv::Point2f"}


def enforce_no_copy_ctor(file_):
    if file_ in EXCLUDE:
        return 0

    cnt = 0
    with open(file_) as f:
        data = f.read()

    for c in CLASSES:
        match = re.search(r"{0} [a-zA-Z0-9_]+ =[\n ]* {0}\(".format(c), data)
        if match is not None:
            print(f"{ALERT}: Please don't use copy ctor if you don't need to")
            print(f"{file_}:\n {c}")
            cnt += 1

    return cnt
