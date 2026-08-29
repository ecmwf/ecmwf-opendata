import json
import logging

import pytest

from ecmwf.opendata import Client, MissingIndexEntriesError


class IndexResponse:
    def __init__(self, entries):
        self.entries = entries

    def raise_for_status(self):
        pass

    def iter_lines(self):
        for entry in self.entries:
            yield json.dumps(entry).encode()


def make_client(monkeypatch, entries):
    client = Client(source="https://example.test")
    monkeypatch.setattr(client, "_robust", lambda call: call)
    monkeypatch.setattr(
        client.session,
        "get",
        lambda *args, **kwargs: IndexResponse(entries),
    )
    monkeypatch.setattr(client, "_download", lambda result: result)
    return client


def entry(param, levelist=None):
    result = {
        "param": param,
        "type": "fc",
        "step": "0",
        "_offset": 0,
        "_length": 100,
    }
    if levelist is not None:
        result["levelist"] = levelist
    return result


def test_strict_retrieval_succeeds_when_all_combinations_exist(monkeypatch):
    client = make_client(
        monkeypatch,
        [
            entry("2t", "500"),
            entry("2t", "850"),
            entry("msl", "500"),
            entry("msl", "850"),
        ],
    )

    result = client.retrieve(
        date="20260101",
        time=0,
        step=0,
        param=["2t", "msl"],
        levelist=[500, 850],
        require_all=True,
    )

    assert len(result.urls) == 1


def test_strict_retrieval_exposes_missing_value(monkeypatch):
    client = make_client(monkeypatch, [entry("2t")])

    with pytest.raises(MissingIndexEntriesError) as error:
        client.retrieve(
            date="20260101",
            time=0,
            step=0,
            param=["2t", "msl"],
            require_all=True,
        )

    assert error.value.missing_combinations == (
        {"param": "msl", "type": "fc", "step": "0"},
    )


def test_strict_retrieval_detects_missing_cross_product(monkeypatch):
    client = make_client(
        monkeypatch,
        [
            entry("2t", "500"),
            entry("2t", "850"),
            entry("msl", "500"),
        ],
    )

    with pytest.raises(MissingIndexEntriesError) as error:
        client.retrieve(
            date="20260101",
            time=0,
            step=0,
            param=["2t", "msl"],
            levelist=[500, 850],
            require_all=True,
        )

    assert error.value.missing_combinations == (
        {"param": "msl", "type": "fc", "step": "0", "levelist": "850"},
    )


def test_default_retrieval_warns_and_continues_for_missing_values(monkeypatch, caplog):
    client = make_client(monkeypatch, [entry("2t")])

    with caplog.at_level(logging.WARNING):
        result = client.retrieve(
            date="20260101",
            time=0,
            step=0,
            param=["2t", "missing"],
        )

    assert len(result.urls) == 1
    assert "No index entries for param=missing" in caplog.messages


def test_strict_failure_happens_before_download(monkeypatch):
    client = make_client(monkeypatch, [entry("2t")])
    downloaded = False

    def download(result):
        nonlocal downloaded
        downloaded = True
        return result

    monkeypatch.setattr(client, "_download", download)

    with pytest.raises(MissingIndexEntriesError):
        client.retrieve(
            date="20260101",
            time=0,
            step=0,
            param=["missing"],
            require_all=True,
        )

    assert not downloaded
