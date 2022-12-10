from typing import Optional, Tuple

# example lines:
"""
"C '\x01f\x02Test1Module.sv\x01l\x0240\x01n\x020\x01page\x02v_user/Test1Module\x01o\x02cover\x01h\x02TOP.Test1Module' 3"
"C '\x01f\x02Test1Module.sv\x01l\x028\x01n\x020\x01page\x02v_user/SubModule1\x01o\x02cover\x01h\x02TOP.Test1Module.c0' 0"
"C '\x01f\x02Test1Module.sv\x01l\x028\x01n\x020\x01page\x02v_user/SubModule1\x01o\x02cover\x01h\x02TOP.Test1Module.c1' 0"
"""
# output:
# - CoverageEntry(Test1Module.sv,40,List(),3)
# - CoverageEntry(Test1Module.sv,8,List(c0),0)
# - CoverageEntry(Test1Module.sv,8,List(c1),0)

cov_t = Tuple[str, int, str, str, str, int]  # file, line, module, type, path, count


def parse_line(line: str) -> Optional[cov_t]:
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
