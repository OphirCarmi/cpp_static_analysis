from common import comment_remover

EXCLUDE = {
}

INCLUDE = {}

ALERT = "BZG360"


def enforce_no_boolean_trap(file_):
    cnt = 0
    if file_ in EXCLUDE:
        return cnt

    if INCLUDE and file_ not in INCLUDE:
        return cnt

    with open(file_) as f:
        data = f.read()

    data = comment_remover(data)
    for y in ("false", "true"):
        for x in (f" {y},", f", {y})", f"({y},", f"({y})"):
            ind = data.find(x)
            if ind >= 0:
                for i in range(1000):
                    if data[ind - i] == "\n":
                        break

                start = ind - i
                end = data.find("\n", ind)
                line = data[start + 1 : end]
                if line.lstrip(" ").startswith("cv::"):
                    continue

                if "json::" in line:
                    continue

                print(f"\n{ALERT} : Boolean trap, use enum")
                print(f"{file_}:\n{line}\n")
                cnt += 1

    return cnt
