import os

import pytest

from ecmwf.opendata import Client


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


@pytest.mark.skipif(
    "ECMWF_OPENDATA_URL" not in os.environ,
    reason="ECMWF_OPENDATA_URL not in os.environ",
)
def test_opendata_1():
    client = Client()
    client.retrieve(
        date=-2,
        time=0,
        step="144-168",
        stream="enfo",
        type="ep",
        levtype="sfc",
        param="tpg100",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 1


@pytest.mark.skipif(
    "ECMWF_OPENDATA_URL" not in os.environ,
    reason="ECMWF_OPENDATA_URL not in os.environ",
)
def test_opendata_2():
    client = Client()
    client.retrieve(
        date=-2,
        time=0,
        step=12,
        stream="enfo",
        type="ef",
        levtype="sfc",
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 51


@pytest.mark.skipif(
    "ECMWF_OPENDATA_URL" not in os.environ,
    reason="ECMWF_OPENDATA_URL not in os.environ",
)
def test_opendata_3():
    client = Client()
    client.retrieve(
        date=-2,
        time=0,
        step=12,
        stream="enfo",
        type="cf",
        levtype="sfc",
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 1


@pytest.mark.skipif(
    "ECMWF_OPENDATA_URL" not in os.environ,
    reason="ECMWF_OPENDATA_URL not in os.environ",
)
def test_opendata_4():
    client = Client()
    client.retrieve(
        date=-2,
        time=0,
        step=12,
        stream="enfo",
        type="pf",
        levtype="sfc",
        param="10u",
        target="data.grib",
    )

    assert count_gribs("data.grib") == 50
