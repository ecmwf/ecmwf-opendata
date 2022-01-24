#!/usr/bin/env python3
import json
import sys
from collections import defaultdict

import eccodes
import requests

from ecmwf.opendata import Client

client = Client()

GROUPS = {
    ("oper", "fc", "pl"): "01 Atmospheric fields on pressure levels",
    ("scda", "fc", "pl"): "01 Atmospheric fields on pressure levels",
    ("enfo", "cf", "pl"): "01 Atmospheric fields on pressure levels",
    ("enfo", "pf", "pl"): "01 Atmospheric fields on pressure levels",
    ("oper", "fc", "sfc"): "02 Atmospheric fields on a single level",
    ("scda", "fc", "sfc"): "02 Atmospheric fields on a single level",
    ("enfo", "cf", "sfc"): "02 Atmospheric fields on a single level",
    ("enfo", "pf", "sfc"): "02 Atmospheric fields on a single level",
    ("wave", "fc", "sfc"): "03 Ocean waves fields",
    ("waef", "cf", "sfc"): "03 Ocean waves fields",
    ("waef", "pf", "sfc"): "03 Ocean waves fields",
    ("scwv", "fc", "sfc"): "03 Ocean waves fields",
    ("enfo", "em", "pl"): "04 Ensemble mean and standard deviation - pressure levels",
    ("enfo", "es", "pl"): "04 Ensemble mean and standard deviation - pressure levels",
    ("enfo", "em", "sfc"): "05 Ensemble mean and standard deviation - single level",
    ("enfo", "es", "sfc"): "05 Ensemble mean and standard deviation - single level",
    (
        "enfo",
        "ep",
        "pl",
    ): "07 Instantaneous weather events - atmospheric fields - 850 hPa",
    (
        "enfo",
        "ep",
        "sfc",
    ): "08 Daily weather events - atmospheric fields - single level",
    ("waef", "ep", "sfc"): "10 Daily weather events - ocean waves fields",
}

groups = defaultdict(set)
seen = set()

with open("index.txt") as f:
    for j, url in enumerate(f):

        url = url.rstrip()

        if (
            "240h" not in url
            and "360h" not in url
            and "90h" not in url
            and "1m" not in url
        ):
            continue

        print(url, file=sys.stderr)

        r = requests.get(url)
        r.raise_for_status()

        lines = []
        for line in r.text.splitlines():
            line = json.loads(line)
            lines.append(line)

        for i, line in enumerate(lines):

            key = tuple(line.get(x) for x in ("type", "stream", "levtype", "param"))
            if key in seen:
                continue

            seen.add(key)

            line["target"] = "data"
            print(line, file=sys.stderr)
            client.retrieve(line)
            with open("data", "rb") as g:
                h = eccodes.codes_new_from_file(g, eccodes.CODES_PRODUCT_GRIB)
                try:
                    key = (
                        eccodes.codes_get_string(h, "stream"),
                        eccodes.codes_get_string(h, "type"),
                        eccodes.codes_get_string(h, "levtype"),
                    )
                    groups[GROUPS[key]].add(
                        (
                            eccodes.codes_get_string(h, "shortName"),
                            eccodes.codes_get_string(h, "nameECMF").replace(
                                "Geopotential Height", "Geopotential height"
                            ),
                            eccodes.codes_get_string(h, "units")
                            .replace("**-1", "<sup>-1</sup>")
                            .replace("**-2", "<sup>-2</sup>"),
                        )
                    )
                finally:
                    eccodes.codes_release(h)


x = {}

for k, v in sorted(groups.items()):
    print()
    print(">", k[3:])
    print()
    x = " | ".join(["Parameter", "Description", "Units"])
    print("|", x, "|")
    x = " | ".join(["---------", "-----------", "-----"])
    print("|", x, "|")
    for r in sorted(v):
        print("|", " | ".join(r), "|")

with open("param.json", "w") as f:
    print(json.dumps(x, indent=4), file=f)
