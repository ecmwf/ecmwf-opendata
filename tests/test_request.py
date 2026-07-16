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

    # Explicit model="aifs-ens" should trigger stream="enfo" default,
    # even when class="od" (which maps to "ifs") is also provided.
    for_urls, _ = client.prepare_request(model="aifs-ens", **{"class": "od"})
    assert for_urls["model"] == ["aifs-ens"]
    assert for_urls["stream"] == ["enfo"]

    # When only class is provided (no explicit model), class should derive the model
    for_urls, _ = client.prepare_request(**{"class": "ai"})
    assert for_urls["model"] == ["aifs-single"]

    # When neither model nor class is provided, client default should be used
    for_urls, _ = client.prepare_request(step=0)
    assert for_urls["model"] == ["ifs"]


if __name__ == "__main__":
    test_request()
