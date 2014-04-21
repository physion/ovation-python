from nose.tools import istest, assert_true

from ovation.conversion import to_set, box_number

@istest
def to_java_set_should_convert_set():
    s = set([1, 2, 'abc'])
    j = to_set(s)
    for item in s:
        assert_true(j.contains(box_number(item)))
