from ecmwf.opendata import Client


def patch_stream(stream, time, type, source="ecmwf"):
    client = Client(source=source, infer_stream_keyword=True)
    args = {"stream": stream, "_H": "%02d" % (time,), "type": type, "model": "ifs"}
    return client.patch_stream(args)


def test_stream_legacy():
    """Legacy behaviour (pre-IFS Cycle 50r1): 06/18 UTC runs use scda/scwv streams."""
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

    # scda/scwv still map through to enfo/waef in legacy mode
    assert patch_stream("scda", 6, "ef") == "enfo"
    assert patch_stream("scda", 18, "ef") == "enfo"
    assert patch_stream("scwv", 6, "ef") == "waef"
    assert patch_stream("scwv", 18, "ef") == "waef"
    assert patch_stream("scda", 6, "ep") == "enfo"
    assert patch_stream("scda", 18, "ep") == "enfo"
    assert patch_stream("scwv", 6, "ep") == "waef"
    assert patch_stream("scwv", 18, "ep") == "waef"


def test_stream_50r1():
    """IFS Cycle 50r1 behaviour (source='ecmwf-testdata'): 06/18 UTC runs remain
    under stream=oper/wave, with no scda/scwv streams."""
    # 00/06/12/18 UTC all stay under oper for fc
    assert patch_stream("oper", 0, "fc", source="ecmwf-testdata") == "oper"
    assert patch_stream("oper", 6, "fc", source="ecmwf-testdata") == "oper"
    assert patch_stream("oper", 12, "fc", source="ecmwf-testdata") == "oper"
    assert patch_stream("oper", 18, "fc", source="ecmwf-testdata") == "oper"

    # 00/06/12/18 UTC all stay under wave for fc
    assert patch_stream("wave", 0, "fc", source="ecmwf-testdata") == "wave"
    assert patch_stream("wave", 6, "fc", source="ecmwf-testdata") == "wave"
    assert patch_stream("wave", 12, "fc", source="ecmwf-testdata") == "wave"
    assert patch_stream("wave", 18, "fc", source="ecmwf-testdata") == "wave"

    # ef type still maps oper -> enfo and wave -> waef
    assert patch_stream("oper", 0, "ef", source="ecmwf-testdata") == "enfo"
    assert patch_stream("oper", 6, "ef", source="ecmwf-testdata") == "enfo"
    assert patch_stream("oper", 12, "ef", source="ecmwf-testdata") == "enfo"
    assert patch_stream("oper", 18, "ef", source="ecmwf-testdata") == "enfo"

    assert patch_stream("wave", 0, "ef", source="ecmwf-testdata") == "waef"
    assert patch_stream("wave", 6, "ef", source="ecmwf-testdata") == "waef"
    assert patch_stream("wave", 12, "ef", source="ecmwf-testdata") == "waef"
    assert patch_stream("wave", 18, "ef", source="ecmwf-testdata") == "waef"

    # ep type still maps oper -> enfo and wave -> waef
    assert patch_stream("oper", 0, "ep", source="ecmwf-testdata") == "enfo"
    assert patch_stream("oper", 6, "ep", source="ecmwf-testdata") == "enfo"
    assert patch_stream("oper", 12, "ep", source="ecmwf-testdata") == "enfo"
    assert patch_stream("oper", 18, "ep", source="ecmwf-testdata") == "enfo"

    assert patch_stream("wave", 0, "ep", source="ecmwf-testdata") == "waef"
    assert patch_stream("wave", 6, "ep", source="ecmwf-testdata") == "waef"
    assert patch_stream("wave", 12, "ep", source="ecmwf-testdata") == "waef"
    assert patch_stream("wave", 18, "ep", source="ecmwf-testdata") == "waef"


# Keep the original test name as an alias so existing test runs aren't broken
def test_stream():
    test_stream_legacy()


if __name__ == "__main__":
    test_stream_legacy()
    test_stream_50r1()
