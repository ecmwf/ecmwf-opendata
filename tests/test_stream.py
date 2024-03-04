from ecmwf.opendata import Client


def patch_stream(stream, time, type):
    client = Client(infer_stream_keyword=True)
    args = {"stream": stream, "_H": "%02d" % (time,), "type": type, "model": "ifs"}
    return client.patch_stream(args)


def test_stream():
    assert patch_stream("oper", 0, "fc") == "oper"
    assert patch_stream("oper", 6, "fc") == "scda"
    assert patch_stream("oper", 12, "fc") == "oper"
    assert patch_stream("oper", 18, "fc") == "scda"

    assert patch_stream("wave", 0, "fc") == "wave"
    assert patch_stream("wave", 6, "fc") == "scwv"
    assert patch_stream("wave", 12, "fc") == "wave"
    assert patch_stream("wave", 18, "fc") == "scwv"

    assert patch_stream("oper", 0, "ef") == "enfo"
    assert patch_stream("oper", 6, "ef") == "enfo"
    assert patch_stream("oper", 12, "ef") == "enfo"
    assert patch_stream("oper", 18, "ef") == "enfo"

    assert patch_stream("wave", 0, "ef") == "waef"
    assert patch_stream("wave", 6, "ef") == "waef"
    assert patch_stream("wave", 12, "ef") == "waef"
    assert patch_stream("wave", 18, "ef") == "waef"

    assert patch_stream("oper", 0, "ep") == "enfo"
    assert patch_stream("oper", 6, "ep") == "enfo"
    assert patch_stream("oper", 12, "ep") == "enfo"
    assert patch_stream("oper", 18, "ep") == "enfo"

    assert patch_stream("wave", 0, "ep") == "waef"
    assert patch_stream("wave", 6, "ep") == "waef"
    assert patch_stream("wave", 12, "ep") == "waef"
    assert patch_stream("wave", 18, "ep") == "waef"


if __name__ == "__main__":
    test_stream()
