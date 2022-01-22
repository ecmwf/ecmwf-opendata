#!/usr/bin/env python
# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import datetime
import re

VALID_DATE = re.compile(r"\d\d\d\d-\d\d-\d\d([T\s]\d\d:\d\d(:\d\d)?)?Z?")


def end_step(p):
    if isinstance(p, str):
        return int(p.split("-")[-1])
    return int(p)


def canonical_time(time):
    time = int(time)
    if time >= 100:
        time //= 100
    return time


def full_date(date, time=None):

    if isinstance(date, datetime.date):
        date = datetime.datetime(date.year, date.month, date.day)

    if isinstance(date, int):
        if date <= 0:
            date = datetime.datetime.utcnow() + datetime.timedelta(days=date)
            date = datetime.datetime(date.year, date.month, date.day)
        else:
            date = datetime.datetime(date // 10000, date % 10000 // 100, date % 100)

    if isinstance(date, str):

        try:
            return full_date(int(date), time)
        except ValueError:
            pass

        if VALID_DATE.match(date):
            date = datetime.datetime.fromisoformat(date)

    if not isinstance(date, datetime.datetime):
        raise ValueError("Invalid date: {} ({})".format(date, type(date)))

    if time is not None:
        time = canonical_time(time)
        date = datetime.datetime(date.year, date.month, date.day, time, 0, 0)

    return date
