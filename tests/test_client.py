#!/usr/bin/env python3
"""Tests for client."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ecmwf.opendata.client import Client, Result


@pytest.mark.parametrize(
    "source, model, forecast_type, stream",
    [
        ("ecmwf", "aifs-single", "fc", "oper"),
        ("azure", "aifs-single", "fc", "oper"),
        ("aws", "aifs-single", "fc", "oper"),
        ("ecmwf", "ifs", "ef", "enfo"),
        ("azure", "ifs", "ef", "enfo"),
        ("aws", "ifs", "ef", "enfo"),
    ],
)
def test_ecmwf_opendata(
    source: str,
    model: str,
    forecast_type: str,
    stream: str,
) -> None:
    temporary_directory = tempfile.TemporaryDirectory(prefix="/tmp/")
    local_file_path = Path(
        f"{temporary_directory.name}/test-{source}-{model}-{forecast_type}-{stream}.grib2"
    )

    client = Client(source=source, model=model, resol="0p25")

    result = client.retrieve(
        type=forecast_type,
        step=list(range(0, 6, 6)),
        param=["2t"],
        target=local_file_path,
        levelist=[],
        stream=stream,
    )

    assert isinstance(result, Result)
    assert isinstance(result.datetime, datetime)
    assert isinstance(result.for_urls, dict)
    assert isinstance(result.for_index, dict)

    Path(local_file_path).unlink()
    temporary_directory.cleanup()
