#!/usr/bin/env python
import json

import requests

seen = {}
x = {}
c = []
OK = {
    ("enfo", "cf"): "ef",
    ("enfo", "pf"): "ef",
    ("waef", "cf"): "ef",
    ("waef", "pf"): "ef",
    ("enfo", "es"): "ep",
    ("enfo", "em"): "ep",
    ("enfo", "es", True): "240",
    ("waef", "es", True): "240",
    ("enfo", "em", True): "240",
    ("waef", "em", True): "240",
    ("enfo", "ep", True): "240",
    ("waef", "ep", True): "240",
    ("enfo", "es", False): "360",
    ("waef", "es", False): "360",
    ("enfo", "em", False): "360",
    ("waef", "em", False): "360",
    ("enfo", "ep", False): "360",
    ("waef", "ep", False): "360",
    "mmsa": "mmsf",
    ("mmsa", "fcmean"): "fc",
}
with open("index.txt") as f:
    for url in f:
        if "mmsf" in url:
            continue
        r = requests.get(url.strip())
        r.raise_for_status()

        line = url.strip().split("/")

        line = line[7:]
        date = line[0]
        time = line[1][:-1] + "00"

        stream = line[3]
        line = line[4].split("-")
        assert line[0] == f"{date}{time}00"
        if line[1][-1] == "m":
            fcmonth = line[1][:-1]
            step = None
        else:
            step = line[1][:-1]
            fcmonth = None
        assert line[2] == stream
        type = line[-1].split(".")[0]

        print(url.strip())
        for p in r.text.splitlines():
            r = json.loads(p)
            ok = True
            ok = ok and r.get("date") == date
            ok = ok and r.get("time") == time

            rstep = r.get("step", "0").split("-")[-1]
            rstep = OK.get(
                (r.get("stream"), r.get("type"), int(rstep) <= 240),
                r.get("step"),
            )

            ok = ok and rstep == step
            ok = ok and r.get("fcmonth") == fcmonth

            rstream = OK.get(r.get("stream"), r.get("stream"))
            ok = ok and rstream == stream

            rtype = OK.get((r.get("stream"), r.get("type")), r.get("type"))
            ok = ok and rtype == type

            if not ok:
                print(url.strip())
                print("Mismatch:", r)

                for a, b, c in (
                    ("date", r.get("date"), date),
                    ("time", r.get("time"), time),
                    ("step", rstep, step),
                    ("fcmonth", r.get("fcmonth"), fcmonth),
                    ("stream", rstream, stream),
                    ("type", rtype, type),
                ):
                    if b != c:
                        print("Mismatch: %r %r %r" % (a, b, c))
                        # assert False
