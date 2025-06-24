from ecmwf.opendata import Client
from ecmwf.opendata.grib import count_gribs

TEST_URL = "https://data.ecmwf.int/forecasts/aifs-ens_testdata/"


def test_aifs_ens_1():
    client = Client(TEST_URL, model="aifs-ens")
    client.retrieve(
        date=-1,
        time=0,
        step=12,
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 51


def test_aifs_ens_2():
    client = Client(TEST_URL, model="aifs-ens")
    client.retrieve(
        date=-1,
        time=0,
        step=12,
        type="cf",
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 1


def test_aifs_ens_3():
    client = Client(TEST_URL, model="aifs-ens")
    client.retrieve(
        date=-1,
        time=0,
        step=12,
        type="pf",
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 50
