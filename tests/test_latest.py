import datetime

from freezegun import freeze_time

from ecmwf.opendata import Client

TEST_URL = "https://get.ecmwf.int/repository/ecmwf-opendata/testing"


@freeze_time("2022-01-21T13:21:34Z")
def test_latest_1():
    client = Client(TEST_URL)
    date = client.latest(
        time=0,
        step="48",
        stream="oper",
        type="fc",
        levtype="sfc",
        param="2t",
        target="data.grib",
    )

    assert date == datetime.date(2022, 1, 20)


# def test_opendata_1():
#     client = Client(TEST_URL)
#     date = client.latest(
#         time=0,
#         step="144-168",
#         stream="enfo",
#         type="ep",
#         levtype="sfc",
#         param="tpg100",
#         target="data.grib",
#     )

#     assert date == datetime.date(2022, 1, 18)


# def test_opendata_2():
#     client = Client(TEST_URL)
#     date = client.latest(
#         time=0,
#         step=12,
#         stream="enfo",
#         type="ef",
#         levtype="sfc",
#         param="10u",
#         target="data.grib",
#     )

#     assert date == datetime.date(2022, 1, 18)


# def test_opendata_3():
#     client = Client(TEST_URL)
#     date = client.latest(
#         step=12,
#         stream="enfo",
#         type="cf",
#         levtype="sfc",
#         param="10u",
#         target="data.grib",
#     )

#     assert date == datetime.datetime(2022, 1, 18, 18)


# def test_opendata_4():
#     client = Client(TEST_URL)
#     date = client.latest(
#         time=0,
#         step=12,
#         stream="enfo",
#         type="pf",
#         levtype="sfc",
#         param="10u",
#         target="data.grib",
#     )

#     assert date == datetime.date(2022, 1, 18)


# def test_opendata_6():
#     client = Client(TEST_URL)
#     date = client.latest(
#         time=0,
#         type="tf",
#         stream="enfo",
#         step=240,
#         target="data.bufr",
#     )

#     assert date == datetime.date(2022, 1, 18)


if __name__ == "__main__":
    test_latest_1()
