import datetime

from freezegun import freeze_time

from ecmwf.opendata import Client

TEST_URL = "https://get.ecmwf.int/repository/ecmwf-opendata/testing"


@freeze_time("2022-01-21t13:21:34Z")
def test_utc():
    assert datetime.datetime.utcnow() == datetime.datetime(2022, 1, 21, 13, 21, 34)


@freeze_time("2022-01-21T13:21:34Z")
def test_latest_00():
    client = Client(TEST_URL)
    date = client.latest(
        time=0,
        step=48,
        stream="oper",
        type="fc",
        levtype="sfc",
        param="2t",
        target="data.grib",
    )

    assert date == datetime.datetime(2022, 1, 20)


@freeze_time("2022-01-21T13:21:34Z")
def test_latest_06():
    client = Client(TEST_URL)
    date = client.latest(
        time=6,
        step=48,
        type="fc",
        levtype="sfc",
        param="2t",
        target="data.grib",
    )

    assert date == datetime.datetime(2022, 1, 20, 6)


@freeze_time("2022-01-21T13:21:34Z")
def test_latest_12():
    client = Client(TEST_URL)
    date = client.latest(
        time=12,
        step=48,
        type="fc",
        levtype="sfc",
        param="2t",
        target="data.grib",
    )

    assert date == datetime.datetime(2022, 1, 20, 12)


@freeze_time("2022-01-20T13:21:34Z")
def test_latest_18():
    client = Client(TEST_URL)
    date = client.latest(
        time=18,
        step=48,
        type="fc",
        levtype="sfc",
        param="2t",
        target="data.grib",
    )

    assert date == datetime.datetime(2022, 1, 19, 18)
