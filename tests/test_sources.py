import os

import pytest

from ecmwf.opendata import Client
from ecmwf.opendata.bufr import count_bufrs
from ecmwf.opendata.grib import count_gribs

SOURCES = os.getenv("SOURCES_TO_TEST", "ecmwf,azure,aws").split(",")


@pytest.mark.parametrize("source", SOURCES)
def test_sources_1(source):
    client = Client(source)

    client.retrieve(
        time=0,
        stream="oper",
        type="fc",
        step=24,
        param="2t",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 1


@pytest.mark.parametrize("source", SOURCES)
def xxx_test_sources_2(source):
    client = Client(source)
    client.retrieve(
        time=0,
        stream="oper",
        type="tf",
        step=240,
        target="data.bufr",
    )

    assert count_gribs("data.grib") == 51


@pytest.mark.parametrize("source", SOURCES)
def test_sources_3(source):
    client = Client(source)
    client.retrieve(
        time=0,
        stream="enfo",
        type="pf",
        param="msl",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 50


@pytest.mark.parametrize("source", SOURCES)
def xxx_test_sources_4(source):
    client = Client(source)
    client.retrieve(
        time=0,
        stream="enfo",
        type="tf",
        step=240,
        target="data.bufr",
    )

    assert count_bufrs("data.bufr") > 0


@pytest.mark.parametrize("source", SOURCES)
def test_sources_6(source):
    client = Client(source)
    client.retrieve(
        time=0,
        stream="enfo",
        type=["es", "em"],
        step=24,
        target="data.grib",
    )
    assert count_gribs("data.grib") == 18
