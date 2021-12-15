import os

import pytest

from ecmwf.opendata import Client


@pytest.mark.skipif(
    "ECMWF_OPENDATA_URL" not in os.environ,
    reason="ECMWF_OPENDATA_URL not in os.environ",
)
def test_opendata():
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
