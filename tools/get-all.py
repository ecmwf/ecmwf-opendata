#!/usr/bin/env python3
import json
import random
import traceback

import eccodes
import requests

from ecmwf.opendata import Client

client = Client()

done = set()

with open("done.txt") as f:
    for url in f:
        url = url.rstrip()
        done.add(url)

ok = open("done.txt", "a")
fail = open("fail.txt", "a")

with open("index.txt") as f:
    for url in f:
        url = url.rstrip()
        if url in done:
            print(url, "DONE")
            continue
        print(url)
        # if "mmsf" in url:
        #     continue
        r = requests.get(url)
        r.raise_for_status()

        try:
            lines = []
            for line in r.text.splitlines():
                line = json.loads(line)
                lines.append(line)

            random.shuffle(lines)

            for i, line in enumerate(lines):
                if i > 20:
                    break
                line["target"] = "data"
                client.retrieve(line)
                with open("data", "rb") as g:
                    h = eccodes.codes_new_from_file(g, eccodes.CODES_PRODUCT_GRIB)
                    try:
                        for k, v in line.items():
                            if k in ["target", "_length", "_offset"]:
                                continue

                            if k == "param":
                                k = "shortName"
                            w = eccodes.codes_get_string(h, k)
                            assert v == w, (v, w)
                    finally:
                        eccodes.codes_release(h)

            print(url, file=ok)
        except Exception as e:
            print(traceback.format_exc())
            print(url, e, file=fail)
