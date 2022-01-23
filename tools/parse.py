#!/usr/bin/env python
from climetlab.utils.factorise import factorise

seen = {}
x = {}
c = []
with open("list.txt") as f:
    for line in f:
        line = line.strip().split("/")
        if line[-1].endswith(".index"):
            continue
        line = line[6:]
        line.pop(1)
        line = [line[0]] + line[2].split("-")[1:]
        if tuple(line) in seen:
            continue
        seen[tuple(line)] = True
        c.append(
            dict(
                time=line[0],
                step=line[1][:-1],
                u=line[1][-1],
                stream=line[2],
                type=line[3].split(".")[0],
                format=line[3].split(".")[1],
            )
        )


def compress(steps):
    if len(steps) < 3:
        return [str(s) for s in sorted(steps)]

    r = []
    d = steps[1] - steps[0]
    start = steps[0]
    prev = steps[0]
    for s in steps[1:]:
        nd = s - prev
        if nd != d:
            r.append("%s-%s-%s" % (start, prev, d))
            start = prev
            d = nd
        prev = s
    r.append("%s-%s-%s" % (start, prev, d))
    return r


p = []
for n in factorise(c).to_list():
    n["step"] = compress(sorted(int(x) for x in n["step"]))
    p.append(n)

print(factorise(p).tree())
