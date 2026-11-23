import datetime
from types import SimpleNamespace
from unittest.mock import Mock

from freezegun import freeze_time

from ecmwf.opendata import Client

TEST_URL = "https://sites.ecmwf.int/repository/ecmwf-opendata/testing"


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


@freeze_time("2026-11-23T13:21:34Z")
def test_latest_skips_run_with_missing_index():
    client = Client(TEST_URL)

    def get_urls(request=None, use_index=False, target=None, **kwargs):
        date = kwargs["date"]
        url = f"https://example.org/{date:%Y%m%d%H}/data.grib2"
        return SimpleNamespace(urls=[url], for_urls={}, for_index={"param": ["2t"]})

    client._get_urls = Mock(side_effect=get_urls)
    client._robust = lambda call: call
    client.session.head = Mock(
        side_effect=[
            Mock(status_code=200),
            Mock(status_code=404),
            Mock(status_code=200),
            Mock(status_code=200),
        ]
    )

    date = client.latest(time=12, step=48, stream="oper", type="fc", param="2t")

    assert date == datetime.datetime(2026, 11, 22, 12)
    assert [call.args[0] for call in client.session.head.call_args_list] == [
        "https://example.org/2026112312/data.grib2",
        "https://example.org/2026112312/data.index",
        "https://example.org/2026112212/data.grib2",
        "https://example.org/2026112212/data.index",
    ]


@freeze_time("2026-11-23T13:21:34Z")
def test_latest_does_not_check_unused_index():
    client = Client(TEST_URL)
    url = "https://example.org/2026112312/data.grib2"
    client._get_urls = Mock(
        return_value=SimpleNamespace(urls=[url], for_urls={}, for_index={})
    )
    client._robust = lambda call: call
    client.session.head = Mock(return_value=Mock(status_code=200))

    date = client.latest(time=12, type="tf")

    assert date == datetime.datetime(2026, 11, 23, 12)
    client.session.head.assert_called_once_with(url, verify=client.verify)


def test_get_urls_only_checks_index_when_retrieving():
    request = {
        "time": 12,
        "step": 48,
        "stream": "oper",
        "type": "fc",
        "levtype": "sfc",
        "param": "2t",
    }

    for use_index in (False, True):
        client = Client(TEST_URL)
        client.latest = Mock(return_value=datetime.datetime(2022, 1, 20, 12))
        client.get_parts = Mock(return_value=[])

        client._get_urls(request=request, use_index=use_index)

        client.latest.assert_called_once()
        assert client.latest.call_args.kwargs["use_index"] is use_index
