from typing import Optional

# example lines:
# "C '\x01f\x02Test1Module.sv\x01l\x0240\x01n\x020\x01page\x02v_user/Test1Module\x01o\x02cover\x01h\x02TOP.Test1Module' 3"
# "C '\x01f\x02Test1Module.sv\x01l\x028\x01n\x020\x01page\x02v_user/SubModule1\x01o\x02cover\x01h\x02TOP.Test1Module.c0' 0"
# "C '\x01f\x02Test1Module.sv\x01l\x028\x01n\x020\x01page\x02v_user/SubModule1\x01o\x02cover\x01h\x02TOP.Test1Module.c1' 0"
# output:
# - CoverageEntry(Test1Module.sv,40,List(),3)
# - CoverageEntry(Test1Module.sv,8,List(c0),0)
# - CoverageEntry(Test1Module.sv,8,List(c1),0)

cov_t = (str, int, str, int) # file, line, path, count

def parseLine(line: str) -> Optional[cov_t]:
    if line.startswith("C '\u0001"):
        return None
    line.split('\'').toList match {
        case List(_, dict, countStr) =>
    val entries = dict.drop(1).split('\u0001').map(_.split('\u0002').toList).map { case Seq(k, v) => k -> v }.toMap
    val count = countStr.trim.toLong
    val path = entries("h").split('.').toList.drop(2).mkString(".")
    val kind = entries("page").split("/").head
    val cov = CoverageEntry(file = entries("f"), line = entries("l").toInt, path = path, count = count)
              // filter out non-user coverage
    kind match {
        case "v_user" => Some(cov)
    case _        => None
    }
    case _ =>
    throw new RuntimeException(s"Unexpected coverage line format: $line")
    }
    }

