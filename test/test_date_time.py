from nose.tools import istest

from ovation.core import date_time, DateTime, DateTimeZone


@istest
def should_create_fully_specified_date():
    expected = DateTime(2013, 12, 2, 3, 2, 1, 15, DateTimeZone.forID('America/Los_Angeles'))
    assert(expected.equals(date_time(2013, 12, 2, 3, 2, 1, 15, 'America/Los_Angeles')))

@istest
def should_create_partially_specified_date():
    expected = DateTime(2013, 12, 2, 0, 0, 0, 0, DateTimeZone.getDefault())
    assert(expected.equals(date_time(2013, 12, 2)))

@istest
def should_create_partially_specified_zoned_date():
    expected = DateTime(2013, 12, 2, 0, 0, 0, 0, DateTimeZone.forID('America/Los_Angeles'))
    assert(expected.equals(date_time(2013, 12, 2, zone='America/Los_Angeles')))