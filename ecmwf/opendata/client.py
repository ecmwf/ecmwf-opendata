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
from collections import defaultdict

import requests
from multiurl import download, robust

from .date import canonical_time, end_step, full_date
from .urls import URLS

LOG = logging.getLogger(__name__)

HOURLY_PATTERN = (
    "{_url}/{_yyyymmdd}/{_H}z/{resol}/{_stream}/"
    "{_yyyymmddHHMMSS}-{step}h-{_stream}-{type}.{_extension}"
)

MONTHLY_PATTERN = (
    "{_url}/{_yyyymmdd}/{_H}z/{resol}/{_stream}/"
    "{_yyyymmddHHMMSS}-{fcmonth}m-{_stream}-{type}.{_extension}"
)

PATTERNS = {"mmsa": MONTHLY_PATTERN}
EXTENSIONS = {"tf": "bufr"}


class Client:
    def __init__(
        self,
        source="ecmwf",
        url=None,
        beta=True,
        preserve_request_order=False,
        auto_stream=True,
    ):
        self._url = url
        self.source = source
        self.beta = beta
        self.preserve_request_order = preserve_request_order
        self.auto_stream = auto_stream

    @property
    def url(self):

        if self._url is None:

            if self.source.startswith("http://") or self.source.startswith("https://"):
                self._url = self.source
            else:
                self._url = URLS[self.source]

        return self._url

    def retrieve(self, request=None, target=None, **kwargs):
        data_urls, target = self._get_urls(
            request,
            target=target,
            use_index=True,
            **kwargs,
        )
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

        date = full_date(0, params.get("time"))

        stop = date - datetime.timedelta(days=1, hours=6)

        while date > stop:
            data_urls, _ = self._get_urls(
                request=None,
                use_index=False,
                date=date,
                **params,
            )
            codes = [robust(requests.head)(url).status_code for url in data_urls]
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

        if "date" not in params:
            params["date"] = self.latest(params)

        if target is None:
            target = params.pop("target", None)

        for_urls, for_index = self.prepare_request(params)

        for_urls["_url"] = [self.url]

        seen = set()
        data_urls = []

        for args in (
            dict(zip(for_urls.keys(), x)) for x in itertools.product(*for_urls.values())
        ):
            pattern = PATTERNS.get(args["stream"], HOURLY_PATTERN)
            date = full_date(args.pop("date", None), args.pop("time", None))
            args["_yyyymmdd"] = date.strftime("%Y%m%d")
            args["_H"] = date.strftime("%H")
            args["_yyyymmddHHMMSS"] = date.strftime("%Y%m%d%H%M%S")
            args["_extension"] = EXTENSIONS.get(args["type"], "grib2")
            args["_stream"] = self.patch_stream(args)

            url = pattern.format(**args)
            if url not in seen:
                data_urls.append(url)
                seen.add(url)

        if for_index and use_index:
            data_urls = self.get_parts(data_urls, for_index)

        return data_urls, target

    def get_parts(self, data_urls, for_index):

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

    def user_to_index(self, key, value, request, for_index):
        FOR_INDEX = {
            ("type", "ef"): ["cf", "pf"],
        }

        return FOR_INDEX.get((key, value), value)

    def user_to_url(self, key, value, request, for_urls):
        FOR_URL = {
            ("type", "cf"): "ef",
            ("type", "pf"): "ef",
            ("type", "em"): "ep",
            ("type", "es"): "ep",
            ("type", "fcmean"): "fc",
            ("stream", "mmsa"): "mmsf",
        }

        if key == "step" and for_urls["type"] == ["ep"]:
            if end_step(value) <= 240:
                return "240"
            else:
                return "360"

        return FOR_URL.get((key, value), value)

    def prepare_request(self, request=None, **kwargs):
        DEFAULTS = dict(
            resol="0p4-beta" if self.beta else "0p4",
            type="fc",
            stream="oper",
            step=0,
            fcmonth=1,
        )

        URL_COMPONENTS = (
            "date",
            "time",
            "resol",
            "stream",
            "type",  # Must be before 'step' in that list
            "step",
            "fcmonth",
        )

        INDEX_COMPONENTS = (
            "param",
            "type",
            "step",
            "fcmonth",
            "number",
            "levelist",
            "levtype",
        )

        CANONICAL = {
            "time": lambda x: str(canonical_time(x)),
        }

        OTHER_STEP = {"mmsa": "step"}

        if request is None:
            params = dict(**kwargs)
        else:
            params = dict(**request)

        for key, value in DEFAULTS.items():
            params.setdefault(key, value)

        params.pop(OTHER_STEP.get(params["stream"], "fcmonth"), None)

        for_urls = defaultdict(list)
        for_index = defaultdict(list)

        for k, v in list(params.items()):
            if not isinstance(v, (list, tuple)):
                v = [v]

            # Return canonical forms
            v = [CANONICAL.get(k, str)(x) for x in v]

            if k.startswith("_"):
                continue

            if k in INDEX_COMPONENTS:
                for values in [self.user_to_index(k, x, params, for_index) for x in v]:
                    if not isinstance(values, (list, tuple)):
                        values = [values]
                    for value in values:
                        if value not in for_index[k]:
                            for_index[k].append(value)

            if k in URL_COMPONENTS:
                for values in [self.user_to_url(k, x, params, for_urls) for x in v]:
                    if not isinstance(values, (list, tuple)):
                        values = [values]
                    for value in values:
                        if value not in for_urls[k]:
                            for_urls[k].append(value)

        if params.get("type") == "tf":
            for_index.clear()

        return (for_urls, for_index)

    def patch_stream(self, args):
        URL_STREAM_MAPPING = {
            ("oper", "06"): "scda",
            ("oper", "18"): "scda",
            ("wave", "06"): "scwv",
            ("wave", "18"): "scwv",
            #
            ("oper", "ef"): "enfo",
            ("wave", "ef"): "waef",
            ("oper", "ep"): "enfo",
            ("wave", "ep"): "waef",
        }
        stream, time, type = args["stream"], args["_H"], args["type"]

        if not self.auto_stream:
            return stream

        stream = URL_STREAM_MAPPING.get((stream, time), stream)
        stream = URL_STREAM_MAPPING.get((stream, type), stream)

        return stream
