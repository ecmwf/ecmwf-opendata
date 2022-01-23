#!/usr/bin/env python3
import json
import traceback
from collections import defaultdict

import requests

from ecmwf.opendata import Client

client = Client()

done = set()

possible_values = defaultdict(set)

with open("index.txt") as f:
    for url in f:
        try:
            url = url.rstrip()
            print(url)
            r = requests.get(url)
            r.raise_for_status()

            lines = []
            for line in r.text.splitlines():
                line = json.loads(line)
                for k, v in line.items():
                    if not k.startswith("_"):
                        possible_values[k].add(v)

        except Exception:
            print(traceback.format_exc())

# print(possible_values)

x = {}

for k, v in possible_values.items():
    x[k] = sorted(v)

print(json.dumps(x, indent=4))
