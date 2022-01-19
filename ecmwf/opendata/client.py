#!/usr/bin/env python
# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import itertools
import json
import logging
import os
import re

import requests
from multiurl import download, robust

from .date import fulldate

LOG = logging.getLogger(__name__)

HOURLY_PATTERN = (
    "{_url}/{_yyyymmdd}/{_H}z/{resol}/{stream}/"
    "{_yyyymmddHHMMSS}-{step}h-{stream}-{type}.{extension}"
)

MONTHLY_PATTERN = (
    "{_url}/{_yyyymmdd}/{_H}z/{resol}/{stream}/"
    "{_yyyymmddHHMMSS}-{fcmonth}m-{stream}-{type}.{extension}"
)

URL_TYPE_MAPPING = {
    "cf": "ef",
    "pf": "ef",
    "em": "ep",
    "es": "ep",
    "fcmean": "fc",
}

URL_STREAM_MAPPING = {
    "mmsa": "mmsf",
    # "wave": "oper",
}


INDEX_TYPE_MAPPING = {"ef": ["cf", "pf"]}

PATTERNS = {"mmsa": MONTHLY_PATTERN}
OTHER_STEP = {"mmsa": "step"}
NO_INDEX = {"tf"}
EXTENSIONS = {"tf": "bufr"}

step_mapping = {}
step_mapping.update({str(x): "240" for x in range(0, 241)})
step_mapping.update({str(x): "360" for x in range(240, 361)})

URL_STEP_MAPPING = {}
URL_STEP_MAPPING["em"] = URL_STEP_MAPPING["es"] = URL_STEP_MAPPING["ep"] = step_mapping

URLS = {}


class Client:
    def __init__(
        self,
        source="ecmwf",
        url=None,
        beta=True,
        preserve_request_order=False,
    ):
        self._url = url if url is not None else os.environ.get("ECMWF_OPENDATA_URL")
        self.source = source
        self.beta = beta
        self.preserve_request_order = preserve_request_order

    @property
    def url(self):
        global URLS

        if self._url is None:

            if self.source.startswith("http://") or self.source.startswith("https://"):
                self._url = self.source
            else:
                if not URLS:
                    dotfile = os.path.expanduser("~/.ecmwf-opendata")
                    if os.path.exists(dotfile):
                        with open(dotfile) as f:
                            URLS = json.load(f)
                self._url = URLS.get(self.source, self.source)

        return self._url

    def retrieve(self, request=None, target=None, **kwargs):
        data_urls, target = self._get_urls(
            request,
            target=target,
            use_index=True,
            **kwargs,
        )
        # print(data_urls)
        download(data_urls, target=target)

    def latest(self, request=None, **kwargs):
        if request is None:
            params = dict(**kwargs)
        else:
            params = dict(**request)
        if "time" not in params:
            delta = datetime.timedelta(hours=6)
        else:
            delta = datetime.timedelta(days=1)
        date = fulldate(0, params.get("time"))
        stop = date - datetime.timedelta(days=1, hours=6)
        while date > stop:
            data_urls, _ = self._get_urls(
                request=None,
                use_index=False,
                date=date,
                **params,
            )
            codes = [robust(requests.head)(url).status_code for url in data_urls]
            # print(codes)
            if len(codes) > 0 and all(c == 200 for c in codes):
                if "time" not in params:
                    return date
                else:
                    return datetime.date(date.year, date.month, date.day)
            date -= delta

        raise ValueError(f"Cannot etablish latest date for {params}")

    def _get_urls(self, request=None, use_index=None, target=None, **kwargs):
        assert use_index in (True, False)
        if request is None:
            params = dict(**kwargs)
        else:
            params = dict(**request)

        defaults = dict(
            resol="0p4-beta" if self.beta else "0p4",
            type="fc",
            stream="oper",
            step=0,
            fcmonth=1,
        )

        for key, value in defaults.items():
            params.setdefault(key, value)

        if "date" not in params:
            params["date"] = self.latest(params)

        params["_url"] = self.url

        params["extension"] = EXTENSIONS.get(params["type"], "grib2")

        if target is None:
            target = params.pop("target", None)

        pattern = PATTERNS.get(params["stream"], HOURLY_PATTERN)

        params.pop(OTHER_STEP.get(params["stream"], "fcmonth"))

        url_components = {"date", "time"}

        for i, p in enumerate(re.split(r"{([^}]*)}", pattern)):
            if i % 2 != 0:
                if not p.startswith("_"):
                    url_components.add(p)

        LOG.debug("url_components are %s", url_components)

        for_urls = {}
        for_index = {}
        for k, v in list(params.items()):
            if not isinstance(v, (list, tuple)):
                v = [v]
            if not k.startswith("_") and k not in url_components:
                for_index[k] = [str(x) for x in v]
                assert len(set(for_index[k])) == len(for_index[k])
            else:
                for_urls[k] = [str(x) for x in v]
                assert len(set(for_urls[k])) == len(for_urls[k])

        self.patch(for_index, for_urls)

        params = None

        seen = set()
        data_urls = []
        for args in (
            dict(zip(for_urls.keys(), x)) for x in itertools.product(*for_urls.values())
        ):
            # print(args)
            date = fulldate(args.pop("date", None), args.pop("time", None))
            args["_yyyymmdd"] = date.strftime("%Y%m%d")
            args["_H"] = date.strftime("%H")
            args["_yyyymmddHHMMSS"] = date.strftime("%Y%m%d%H%M%S")
            url = pattern.format(**args)
            if url not in seen:
                data_urls.append(url)
                seen.add(url)

        if for_index and use_index:
            data_urls = self.get_parts(data_urls, for_index)

        return data_urls, target

    def get_parts(self, data_urls, for_index):

        # print(for_index)

        count = len(for_index)
        result = []
        line = None

        for url in data_urls:
            base, _ = os.path.splitext(url)
            index_url = f"{base}.index"
            r = robust(requests.get)(index_url)
            r.raise_for_status()

            parts = []
            for line in r.iter_lines():
                line = json.loads(line)
                matches = []
                for i, (name, values) in enumerate(for_index.items()):
                    idx = line.get(name)
                    if idx in values:
                        if self.preserve_request_order:
                            for j, v in enumerate(values):
                                if v == idx:
                                    matches.append((i, j))
                        else:
                            matches.append(line["_offset"])

                if len(matches) == count:
                    parts.append((tuple(matches), (line["_offset"], line["_length"])))

            if parts:
                result.append((url, tuple(p[1] for p in sorted(parts))))

        assert len(result) > 0, (for_index, line)
        return result

    def patch(self, for_index, for_urls):
        def last_step(p):
            if isinstance(p, str):
                return p.split("-")[-1]
            return str(p)

        assert len(for_urls["type"]) == 1, (
            for_urls["type"],
            len(for_urls["type"]),
        )  # For now

        for step in ("step",):  # "fcmonth"):
            if step in for_urls:
                for_index[step] = for_urls[step]

        if for_urls["type"][0] in URL_STEP_MAPPING:
            for_urls["step"] = [
                URL_STEP_MAPPING[for_urls["type"][0]][last_step(t)]
                for t in for_urls["step"]
            ]

        for_index["type"] = INDEX_TYPE_MAPPING.get(
            for_urls["type"][0], for_urls["type"]
        )

        for_urls["type"] = [URL_TYPE_MAPPING.get(t, t) for t in for_urls["type"]]
        for_urls["stream"] = [URL_STREAM_MAPPING.get(s, s) for s in for_urls["stream"]]

        for t in for_urls["type"]:
            if t in NO_INDEX:
                for_index.clear()
