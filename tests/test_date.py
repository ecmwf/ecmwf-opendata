import datetime

from freezegun import freeze_time

from ecmwf.opendata.date import canonical_time, end_step, full_date


@freeze_time("2022-01-21T13:21:34Z")
def test_date_1():
    assert full_date("20010101") == datetime.datetime(2001, 1, 1)
    assert full_date(20010101) == datetime.datetime(2001, 1, 1)
    assert full_date("2001-01-01") == datetime.datetime(2001, 1, 1)

    assert full_date(0) == datetime.datetime(2022, 1, 21)
    assert full_date(-10) == datetime.datetime(2022, 1, 11)

    assert full_date("20010101", 0) == datetime.datetime(2001, 1, 1)
    assert full_date(20010101, 0) == datetime.datetime(2001, 1, 1)
    assert full_date("2001-01-01", 0) == datetime.datetime(2001, 1, 1)

    assert full_date(0, 0) == datetime.datetime(2022, 1, 21)
    assert full_date(-10, 0) == datetime.datetime(2022, 1, 11)

    assert full_date("20010101", 12) == datetime.datetime(2001, 1, 1, 12)
    assert full_date(20010101, 12) == datetime.datetime(2001, 1, 1, 12)
    assert full_date("2001-01-01", 12) == datetime.datetime(2001, 1, 1, 12)

    assert full_date(0, 12) == datetime.datetime(2022, 1, 21, 12)
    assert full_date(-10, 12) == datetime.datetime(2022, 1, 11, 12)

    assert full_date("20010101", "18") == datetime.datetime(2001, 1, 1, 18)
    assert full_date(20010101, "18") == datetime.datetime(2001, 1, 1, 18)
    assert full_date("2001-01-01", "18") == datetime.datetime(2001, 1, 1, 18)

    assert full_date(0, "18") == datetime.datetime(2022, 1, 21, 18)
    assert full_date(-10, "18") == datetime.datetime(2022, 1, 11, 18)

    assert full_date("20010101", "06") == datetime.datetime(2001, 1, 1, 6)
    assert full_date(20010101, "06") == datetime.datetime(2001, 1, 1, 6)
    assert full_date("2001-01-01", "06") == datetime.datetime(2001, 1, 1, 6)

    assert full_date(0, "06") == datetime.datetime(2022, 1, 21, 6)
    assert full_date(-10, "06") == datetime.datetime(2022, 1, 11, 6)

    assert full_date("20010101", "0600") == datetime.datetime(2001, 1, 1, 6)
    assert full_date(20010101, "0600") == datetime.datetime(2001, 1, 1, 6)
    assert full_date("2001-01-01", "0600") == datetime.datetime(2001, 1, 1, 6)

    assert full_date(0, "0600") == datetime.datetime(2022, 1, 21, 6)
    assert full_date(-10, "0600") == datetime.datetime(2022, 1, 11, 6)

    assert full_date("20010101", "1200") == datetime.datetime(2001, 1, 1, 12)
    assert full_date(20010101, "1200") == datetime.datetime(2001, 1, 1, 12)
    assert full_date("2001-01-01", "1200") == datetime.datetime(2001, 1, 1, 12)

    assert full_date(0, "1200") == datetime.datetime(2022, 1, 21, 12)
    assert full_date(-10, "1200") == datetime.datetime(2022, 1, 11, 12)

    assert full_date("20010101", "18") == datetime.datetime(2001, 1, 1, 18)
    assert full_date(20010101, "18") == datetime.datetime(2001, 1, 1, 18)
    assert full_date("2001-01-01", "18") == datetime.datetime(2001, 1, 1, 18)

    assert full_date(0, "18") == datetime.datetime(2022, 1, 21, 18)
    assert full_date(-10, "18") == datetime.datetime(2022, 1, 11, 18)

    assert full_date("2022-01-25 12:00:00") == datetime.datetime(2022, 1, 25, 12)
    assert full_date("2022-01-25 12:00:00", "18") == datetime.datetime(2022, 1, 25, 18)
    assert full_date("2022-01-25T12:00:00") == datetime.datetime(2022, 1, 25, 12)


def test_date_2():
    assert full_date(datetime.datetime(2000, 1, 1, 6)) == datetime.datetime(
        2000, 1, 1, 6
    )
    assert full_date(datetime.datetime(2000, 1, 1, 6), 12) == datetime.datetime(
        2000, 1, 1, 12
    )
    assert full_date(datetime.date(2000, 1, 1)) == datetime.datetime(2000, 1, 1)
    assert full_date(datetime.date(2000, 1, 1), 12) == datetime.datetime(2000, 1, 1, 12)


def test_time():
    assert canonical_time(0) == 0
    assert canonical_time(6) == 6
    assert canonical_time(12) == 12
    assert canonical_time(18) == 18

    assert canonical_time("0") == 0
    assert canonical_time("6") == 6
    assert canonical_time("12") == 12
    assert canonical_time("18") == 18

    assert canonical_time("00") == 0
    assert canonical_time("06") == 6
    assert canonical_time("12") == 12
    assert canonical_time("18") == 18

    assert canonical_time(1200) == 12
    assert canonical_time(1800) == 18

    assert canonical_time("0000") == 0
    assert canonical_time("0600") == 6
    assert canonical_time("1200") == 12
    assert canonical_time("1800") == 18

    assert canonical_time(datetime.time(12)) == 12


def test_step():
    assert end_step(24) == 24
    assert end_step("24") == 24
    assert end_step("12-24") == 24
