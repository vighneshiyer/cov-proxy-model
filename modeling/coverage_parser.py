from typing import Tuple

cov_t = Tuple[str, int, str, str, str, int]  # file, line, module, type, path, count


def parse_line(line: str) -> cov_t:
    sections_large = line.split(' ')
    assert sections_large[0] == "C"
    count = int(sections_large[2])

    data = sections_large[1].split('\u0001')[1:]

    file = data[0].split('\u0002')[1]
    line = int(data[1].split('\u0002')[1])
    module = data[3].split('\u0002')[1].split('/')[1]
    tpe = data[4].split('\u0002')[1]
    path = data[-1].split('\u0002')[1][:-1]

    return file, line, module, tpe, path, count
