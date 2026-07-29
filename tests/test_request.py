from ecmwf.opendata import Client


def test_request():
    client = Client(preserve_request_order=True)

    for_urls, _ = client.prepare_request(step="0/to/120")

    assert for_urls["step"] == [str(s) for s in range(0, 121)]

    for_urls, _ = client.prepare_request(step="0/to/120/by/6")

    assert for_urls["step"] == [str(s) for s in range(0, 121, 6)]

    for_urls, _ = client.prepare_request(time="0/to/18")

    assert for_urls["time"] == [str(s) for s in range(0, 24, 6)]

    for_urls, _ = client.prepare_request(date="20000101/to/20000131")

    assert for_urls["date"] == [str(s) for s in range(20000101, 20000132)]

    for_urls, _ = client.prepare_request(date="20000101/to/20000131/by/7")

    assert for_urls["date"] == [str(s) for s in range(20000101, 20000132, 7)]


def test_explicit_model_not_overridden_by_class():
    """Test that an explicit model in retrieve takes precedence over class-derived model.

    Previously passing model="aifs-ens" with class="od" would prevent the automatic stream="enfo"
    default from being applied because class="od" would override model to "ifs".
    """
    client = Client(model="ifs")

    for_urls, _ = client.prepare_request(model="aifs-ens", **{"class": "od"})
    assert for_urls["model"] == ["aifs-ens"]
    assert for_urls["stream"] == ["enfo"]

    for_urls, _ = client.prepare_request(**{"class": "ai"})
    assert for_urls["model"] == ["aifs-single"]

    for_urls, _ = client.prepare_request(step=0)
    assert for_urls["model"] == ["ifs"]


def test_aifs_ens_respects_explicit_stream():
    """Test that an explicit stream for aifs-ens is respected.

    Previously passing model="aifs-ens" always forced stream="enfo",
    so the wave ensemble (stream="waef") could not be requested: the
    request silently resolved to the enfo file instead.
    """
    client = Client(model="aifs-ens")

    # Explicit stream="waef" should be honoured, not overwritten to enfo
    for_urls, _ = client.prepare_request(stream="waef", type="cf", step=24)
    assert for_urls["stream"] == ["waef"]

    # With no stream given, aifs-ens should still default to enfo
    for_urls, _ = client.prepare_request(type="cf", step=24)
    assert for_urls["stream"] == ["enfo"]


if __name__ == "__main__":
    test_request()