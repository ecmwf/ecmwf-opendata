#!/usr/bin/env python
# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import os
import stat
import warnings

DOT_ECMWF_OPENDATA = os.path.expanduser("~/.ecmwf-opendata")

URLS = {
    "aws": "https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com",
    "azure": "https://ai4edataeuwest.blob.core.windows.net/ecmwf",
    "diss": "https://diss.ecmwf.int/ecpds",
    "ecmwf": "https://data.ecmwf.int/forecasts",
    "ecmwf-esuites": "https://xdiss.ecmwf.int/ecpds/home/opendata",
    "ecmwf-testdata": "https://data.ecmwf.int/forecasts/testdata",
    "google": "https://storage.googleapis.com/ecmwf-open-data",
}

_CREDENTIALS = {}


def _check_config_permissions(path, has_credentials=False):
    """Warn if config file with credentials is group/world-readable."""
    if not has_credentials:
        return
    try:
        mode = os.stat(path).st_mode
        if mode & (stat.S_IRGRP | stat.S_IROTH):
            warnings.warn(
                f"{path} contains credentials and is readable by group/others. "
                f"Run: chmod 600 {path}",
                stacklevel=3,
            )
    except OSError:
        pass


if os.path.exists(DOT_ECMWF_OPENDATA):
    with open(DOT_ECMWF_OPENDATA) as f:
        _config = json.load(f)
    _creds = _config.pop("credentials", {})
    _CREDENTIALS.update(_creds)
    URLS.update(_config)
    _check_config_permissions(DOT_ECMWF_OPENDATA, has_credentials=bool(_creds))

if "ECMWF_OPENDATA_URLS" in os.environ:
    URLS.update(json.loads(os.environ["ECMWF_OPENDATA_URLS"]))


def get_credentials(source_name):
    """Return credentials dict for a source, or empty dict.

    Priority: environment variables > config file.
    """
    prefix = f"ECMWF_{source_name.upper().replace('-', '_')}"
    username = os.environ.get(f"{prefix}_USERNAME")
    password = os.environ.get(f"{prefix}_PASSWORD")
    if username and password:
        return {"username": username, "password": password}
    return dict(_CREDENTIALS.get(source_name, {}))
