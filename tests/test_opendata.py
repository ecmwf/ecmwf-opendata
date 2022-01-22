import eccodes
from freezegun import freeze_time

from ecmwf.opendata import Client
from ecmwf.opendata.grib import count_gribs, grib_index

TEST_URL = "https://get.ecmwf.int/repository/ecmwf-opendata/testing"


@freeze_time("2022-01-21t13:21:34z")
def xx_test_opendata_1():
    client = Client(TEST_URL)
    client.retrieve(
        date=-1,
        time=0,
        step="144-168",
        stream="enfo",
        type="ep",
        levtype="sfc",
        param="tpg100",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 1


@freeze_time("2022-01-21t13:21:34z")
def test_opendata_2():
    client = Client(TEST_URL)
    client.retrieve(
        date=-1,
        time=0,
        step=12,
        stream="enfo",
        type="ef",
        levtype="sfc",
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 51


@freeze_time("2022-01-21t13:21:34z")
def test_opendata_3():
    client = Client(TEST_URL)
    client.retrieve(
        date=-1,
        time=0,
        step=12,
        stream="enfo",
        type="cf",
        levtype="sfc",
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 1


@freeze_time("2022-01-21t13:21:34z")
def test_opendata_4():
    client = Client(TEST_URL)
    client.retrieve(
        date=-1,
        time=0,
        step=12,
        stream="enfo",
        type="pf",
        levtype="sfc",
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 50


@freeze_time("2022-01-21t13:21:34z")
def xx_test_opendata_6():
    client = Client(TEST_URL)
    client.retrieve(
        date=-1,
        time=0,
        type="tf",
        stream="enfo",
        step=240,
        target="data.bufr",
    )

    with open("data.bufr", "rb") as f:
        assert f.read(4) == b"BUFR"
