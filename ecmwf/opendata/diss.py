#!/usr/bin/env python
# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

"""ECMWF DISS (Dissemination Data Store) client for SOFF forecast data."""

import datetime
import logging
import os
from typing import Optional
from urllib.parse import urlparse

import requests
from multiurl import download

from .date import full_date
from .urls import URLS, get_credentials

LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# WMO filename encoding
# ---------------------------------------------------------------------------

# DISS file type prefixes
DISS_PREFIXES = {
    "model": "FMD",
    "pressure": "FPD",
    "surface": "FSD",
    "amdar": "AND",
}

# Reverse lookup
DISS_PREFIX_TO_TYPE = {v: k for k, v in DISS_PREFIXES.items()}

DISS_HOST = "diss.ecmwf.int"
DISS_BASE_URL = "https://diss.ecmwf.int/ecpds/data/file"
DISS_LIST_URL = "https://diss.ecmwf.int/ecpds/data/list"


def build_diss_filename(
    file_type: str,
    analysis_date: datetime.datetime,
    step: int,
    seq: Optional[int] = None,
) -> str:
    """Build a WMO-style DISS filename.

    Parameters
    ----------
    file_type : str
        One of "model", "pressure", "surface", "amdar".
    analysis_date : datetime.datetime
        Analysis date/time (e.g. 2026-06-23 00:00).
    step : int
        Forecast step in hours (0-90).
    seq : int, optional
        Sequence number. Defaults to 011 for step=0, 001 otherwise.

    Returns
    -------
    str
        WMO-style filename, e.g. "FSD06230000062318001".
    """
    if file_type not in DISS_PREFIXES:
        raise ValueError(
            f"Unknown file_type {file_type!r}. "
            f"Must be one of: {list(DISS_PREFIXES.keys())}"
        )

    prefix = DISS_PREFIXES[file_type]
    valid_date = analysis_date + datetime.timedelta(hours=step)

    if seq is None:
        seq = 11 if step == 0 else 1

    mmdd = analysis_date.strftime("%m%d")
    hhmm = analysis_date.strftime("%H%M")
    mmdd_valid = valid_date.strftime("%m%d")
    hh_valid = valid_date.strftime("%H")

    return f"{prefix}{mmdd}{hhmm}{mmdd_valid}{hh_valid}{seq:03d}"


def parse_diss_filename(filename: str) -> dict:
    """Parse a WMO-style DISS filename into components.

    Returns dict with keys: prefix, file_type, analysis_mmdd, analysis_hhmm,
    valid_mmdd, valid_hh, seq.
    """
    if len(filename) < 20:
        raise ValueError(f"Filename too short to be a valid DISS filename: {filename!r}")

    prefix = filename[:3]
    file_type = DISS_PREFIX_TO_TYPE.get(prefix)
    return {
        "prefix": prefix,
        "file_type": file_type,
        "analysis_mmdd": filename[3:7],
        "analysis_hhmm": filename[7:11],
        "valid_mmdd": filename[11:15],
        "valid_hh": filename[15:17],
        "seq": int(filename[17:20]),
    }


# ---------------------------------------------------------------------------
# Scoped authentication
# ---------------------------------------------------------------------------


class DissAuth(requests.auth.AuthBase):
    """HTTP Basic Auth scoped to the DISS host only.

    Credentials are only injected for requests targeting diss.ecmwf.int,
    preventing accidental credential leakage to other hosts via redirects.
    """

    def __init__(self, username: str, password: str):
        self._auth = requests.auth.HTTPBasicAuth(username, password)

    def __call__(self, r):
        if urlparse(r.url).hostname == DISS_HOST:
            return self._auth(r)
        return r

    def __repr__(self):
        return "DissAuth(username=<redacted>)"


# ---------------------------------------------------------------------------
# DISS Client
# ---------------------------------------------------------------------------


class DissClient:
    """Client for downloading SOFF forecast data from ECMWF DISS.

    Parameters
    ----------
    username : str, optional
        DISS username. If not provided, read from env var
        ECMWF_DISS_USERNAME or ~/.ecmwf-opendata config.
    password : str, optional
        DISS password. Same fallback chain as username.
    base_url : str, optional
        Override the DISS file endpoint base URL.
    verify : bool, optional
        Verify SSL certificates (default True).
    """

    def __init__(
        self,
        username: str = None,
        password: str = None,
        base_url: str = None,
        verify: bool = True,
    ):
        creds = get_credentials("diss")
        self.username = username or creds.get("username")
        self.password = password or creds.get("password")

        if not self.username or not self.password:
            raise ValueError(
                "DISS credentials required. Provide username/password directly, "
                "set ECMWF_DISS_USERNAME/ECMWF_DISS_PASSWORD environment variables, "
                "or add credentials to ~/.ecmwf-opendata config file."
            )

        # Base URL: explicit arg > URLS dict > hardcoded default
        self.base_url = base_url or URLS.get("diss", DISS_BASE_URL)
        # Ensure base_url points to the file endpoint
        if self.base_url.endswith("/ecpds"):
            self.base_url = f"{self.base_url}/data/file"
            self.list_url = self.base_url.replace("/data/file", "/data/list")
        else:
            self.list_url = DISS_LIST_URL

        self.verify = verify

        self.session = requests.Session()
        self.session.auth = DissAuth(self.username, self.password)

    def _build_url(self, date: datetime.datetime, filename: str) -> str:
        """Build full DISS download URL."""
        yyyymmdd = date.strftime("%Y%m%d")
        return f"{self.base_url}/{yyyymmdd}/{filename}"

    def list_files(self, date, file_type: str = None) -> list:
        """List available files for a given date.

        Parameters
        ----------
        date : int, str, or datetime
            Analysis date (e.g. 20260623, "2026-06-23", or datetime).
        file_type : str, optional
            Filter by type: "model", "pressure", "surface", "amdar".

        Returns
        -------
        list[dict]
            File metadata from the DISS JSON listing API.
        """
        dt = full_date(date, 0)
        yyyymmdd = dt.strftime("%Y%m%d")
        url = f"{self.list_url}/{yyyymmdd}/"
        r = self.session.get(
            url,
            headers={"Accept": "application/json"},
            verify=self.verify,
        )
        r.raise_for_status()
        files = r.json()

        if file_type is not None:
            prefix = DISS_PREFIXES.get(file_type)
            if prefix is None:
                raise ValueError(
                    f"Unknown file_type {file_type!r}. "
                    f"Must be one of: {list(DISS_PREFIXES.keys())}"
                )
            files = [f for f in files if f["name"].startswith(prefix)]

        return files

    def download(
        self,
        target: str,
        date=None,
        time: int = 0,
        file_type: str = "surface",
        step=None,
        steps=None,
        filename: str = None,
        filenames: list = None,
    ):
        """Download SOFF data files from DISS.

        Specify files by either:
        - (date, time, file_type, step/steps) to auto-build filenames, or
        - (date, filename/filenames) to download specific named files.

        Parameters
        ----------
        target : str
            Local file path to save to. For multiple files, treated as a
            directory and each file is saved with its DISS filename.
        date : int, str, or datetime
            Analysis date. Required.
        time : int
            Analysis hour (default 0, DISS currently only serves 00Z).
        file_type : str
            One of "model", "pressure", "surface", "amdar".
        step : int, optional
            Single forecast step in hours.
        steps : list[int], optional
            Multiple forecast steps.
        filename : str, optional
            Exact DISS filename to download.
        filenames : list[str], optional
            Multiple exact DISS filenames.

        Returns
        -------
        list[str]
            List of local file paths written.
        """
        if date is None:
            raise ValueError("date is required")

        dt = full_date(date, time)
        urls = []

        if filename is not None:
            urls.append(self._build_url(dt, filename))
        elif filenames is not None:
            urls.extend(self._build_url(dt, f) for f in filenames)
        elif step is not None or steps is not None:
            step_list = [step] if step is not None else steps
            for s in step_list:
                fname = build_diss_filename(file_type, dt, s)
                urls.append(self._build_url(dt, fname))
        else:
            raise ValueError("Specify step/steps or filename/filenames")

        # Single file: download directly to target
        if len(urls) == 1:
            download(
                urls[0],
                target=target,
                verify=self.verify,
                session=self.session,
            )
            return [target]
        # Multiple files: download each to target directory
        else:
            os.makedirs(target, exist_ok=True)
            paths = []
            for url in urls:
                fname = url.rsplit("/", 1)[-1]
                fpath = os.path.join(target, fname)
                download(
                    url,
                    target=fpath,
                    verify=self.verify,
                    session=self.session,
                )
                paths.append(fpath)
            return paths
