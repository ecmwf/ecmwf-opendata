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


if __name__ == "__main__":
    test_request()
