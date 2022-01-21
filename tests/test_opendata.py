from freezegun import freeze_time

from ecmwf.opendata import Client

TEST_URL = "https://get.ecmwf.int/repository/ecmwf-opendata/testing"


def get(f, count):
    n = 0
    for i in range(0, count):
        n = n * 256 + int(f.read(1)[0])
    return n


def count_gribs(path):
    count = 0
    with open(path, "rb") as f:
        while True:
            offset = f.tell()
            code = f.read(4)

            if len(code) < 4:
                break

            if code != b"GRIB":
                f.seek(offset + 1)
                continue

            length = get(f, 3)
            edition = get(f, 1)
            assert edition == 2

            length = get(f, 8)

            f.seek(offset + length - 4)
            code = f.read(4)
            assert code == b"7777", code

            count += 1

    return count


@freeze_time("2022-01-21 13:21:34")
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


@freeze_time("2022-01-21 13:21:34")
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


@freeze_time("2022-01-21 13:21:34")
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


@freeze_time("2022-01-21 13:21:34")
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


@freeze_time("2022-01-21 13:21:34")
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
