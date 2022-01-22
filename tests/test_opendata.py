from freezegun import freeze_time

from ecmwf.opendata import Client
from ecmwf.opendata.bufr import count_bufrs
from ecmwf.opendata.grib import count_gribs

TEST_URL = "https://get.ecmwf.int/repository/ecmwf-opendata/testing"

"""
format=bufr, type=tf
   HH=00/12
      stream=enfo/oper, step=240h
   HH=06/18
      stream=enfo, step=144h
      stream=scda, step=90h

format=grib2
   HH=00/12
       stream=enfo/waef
          type=ef, step=0h to 144h by 3h, 144h to 360h by 6h
          type=ep, step=240h/360h
  stream=oper, wave
       type=fc, step=0h to 144h by 3h, 144h to 360h by 6h
     HH=06/18
       stream=enfo/waef
          type=ef, step=0h to 144h by 3h
       stream= scda /scwv
          type=fc, step=0h to 90h by 3h
     HH=00
       stream=mmsf, type=fc, u=m, step=1m to 7m
"""


@freeze_time("2022-01-21t13:21:34z")
def xxx_test_opendata_1():
    client = Client(TEST_URL)
    client.retrieve(
        time=0,
        step=240,
        stream="oper",
        type="tf",
        levtype="sfc",
        param="tpg100",
        target="data.bufr",
    )

    assert count_bufrs("data.bufr") > 0


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
