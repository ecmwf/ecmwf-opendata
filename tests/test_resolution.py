#!/usr/bin/env python3
"""Tests for the resol keyword and the 0p1 sfc/pl file split."""

import logging

import pytest

from ecmwf.opendata import Client
from ecmwf.opendata.utils import ONCE

URL = "https://data.ecmwf.int/forecasts"
DATE = 20261009


def urls(client, **kwargs):
    kwargs.setdefault("date", DATE)
    kwargs.setdefault("time", 0)
    return client._get_urls(use_index=False, **kwargs).urls


def test_default_resolution_is_0p25():
    assert urls(Client(), step=6) == [
        f"{URL}/20261009/00z/ifs/0p25/oper/20261009000000-6h-oper-fc.grib2"
    ]


def test_0p25_ignores_levtype_for_files():
    assert urls(Client(), step=6, levtype="pl") == [
        f"{URL}/20261009/00z/ifs/0p25/oper/20261009000000-6h-oper-fc.grib2"
    ]


@pytest.mark.parametrize(
    "client, request_resol",
    [
        (Client(resol="0p1"), None),
        (Client(), "0p1"),
    ],
)
def test_0p1_without_levtype_returns_sfc_and_pl(client, request_resol):
    kwargs = {"resol": request_resol} if request_resol else {}
    assert urls(client, step=6, **kwargs) == [
        f"{URL}/20261009/00z/ifs/0p1/oper/20261009000000-6h-oper-fc-sfc.grib2",
        f"{URL}/20261009/00z/ifs/0p1/oper/20261009000000-6h-oper-fc-pl.grib2",
    ]


@pytest.mark.parametrize("levtype", ["sfc", "pl"])
def test_0p1_levtype_selects_file(levtype):
    assert urls(Client(), resol="0p1", step=6, levtype=levtype) == [
        f"{URL}/20261009/00z/ifs/0p1/oper/20261009000000-6h-oper-fc-{levtype}.grib2"
    ]


def test_0p1_levtype_list_selects_both_files():
    assert urls(Client(), resol="0p1", step=6, levtype=["pl", "sfc"]) == [
        f"{URL}/20261009/00z/ifs/0p1/oper/20261009000000-6h-oper-fc-pl.grib2",
        f"{URL}/20261009/00z/ifs/0p1/oper/20261009000000-6h-oper-fc-sfc.grib2",
    ]


def test_0p1_sol_uses_sfc_file():
    assert urls(Client(), resol="0p1", step=6, levtype="sol") == [
        f"{URL}/20261009/00z/ifs/0p1/oper/20261009000000-6h-oper-fc-sfc.grib2"
    ]
    assert urls(Client(), resol="0p1", step=6, levtype=["sfc", "sol"]) == [
        f"{URL}/20261009/00z/ifs/0p1/oper/20261009000000-6h-oper-fc-sfc.grib2"
    ]


def test_0p1_ensemble():
    assert urls(Client(), resol="0p1", stream="enfo", step=6) == [
        f"{URL}/20261009/00z/ifs/0p1/enfo/20261009000000-6h-enfo-ef-sfc.grib2",
        f"{URL}/20261009/00z/ifs/0p1/enfo/20261009000000-6h-enfo-ef-pl.grib2",
    ]


def test_0p1_ensemble_products():
    assert urls(Client(), resol="0p1", stream="enfo", type="ep", step=240) == [
        f"{URL}/20261009/00z/ifs/0p1/enfo/20261009000000-240h-enfo-ep-sfc.grib2",
        f"{URL}/20261009/00z/ifs/0p1/enfo/20261009000000-240h-enfo-ep-pl.grib2",
    ]


@pytest.mark.parametrize(
    "stream, type, expected",
    [
        ("wave", "fc", "wave/20261009000000-6h-wave-fc-sfc.grib2"),
        ("waef", "cf", "waef/20261009000000-6h-waef-ef-sfc.grib2"),
        ("waef", "ep", "waef/20261009000000-240h-waef-ep-sfc.grib2"),
    ],
)
def test_0p1_wave_only_has_sfc(stream, type, expected):
    step = 240 if type == "ep" else 6
    assert urls(Client(), resol="0p1", stream=stream, type=type, step=step) == [
        f"{URL}/20261009/00z/ifs/0p1/{expected}"
    ]


def test_0p1_06z_run():
    assert urls(Client(), resol="0p1", time=6, step=6, levtype="sfc") == [
        f"{URL}/20261009/06z/ifs/0p1/oper/20261009060000-6h-oper-fc-sfc.grib2"
    ]


def test_tf_always_uses_0p25():
    assert urls(Client(resol="0p1"), type="tf", step=240) == [
        f"{URL}/20261009/00z/ifs/0p25/oper/20261009000000-240h-oper-tf.bufr"
    ]


def test_index_url_follows_split_file():
    # get_parts derives the index url from the data url, so the
    # split files must map to their own "-sfc.index"/"-pl.index"
    for url in urls(Client(), resol="0p1", step=6):
        assert url.endswith(("-sfc.grib2", "-pl.grib2"))
        assert url.replace(".grib2", ".index").endswith(("-sfc.index", "-pl.index"))


@pytest.fixture
def fresh_warnings():
    # warning_once only logs each message once per process
    ONCE.clear()


def test_unknown_resolution_warns(caplog, fresh_warnings):
    with caplog.at_level(logging.WARNING):
        Client().prepare_request(resol="0p01", step=6)
    assert "Unknown value '0p01' for keyword 'resol'" in caplog.text


def test_resolution_mismatch_warns(caplog, fresh_warnings):
    with caplog.at_level(logging.WARNING):
        for_urls, _ = Client(resol="0p25").prepare_request(resol="0p1", step=12)
    assert for_urls["resol"] == ["0p1"]
    assert "does not match the client resolution" in caplog.text


@pytest.mark.parametrize("model", ["aifs-single", "aifs-ens"])
def test_0p1_non_ifs_model_raises(model):
    with pytest.raises(ValueError, match="only available for model 'ifs'"):
        Client(model=model).prepare_request(resol="0p1", step=18)

    with pytest.raises(ValueError, match="only available for model 'ifs'"):
        Client(resol="0p1").prepare_request(model=model, step=18)
