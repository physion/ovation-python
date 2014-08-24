import collections
import six
from nose.tools import istest, assert_equals

from ovation import autoclass
from ovation.core import Maps
from ovation.conversion import to_map, to_dict, box_number


@istest
def to_dict_should_convert_flat_map():
    m = Maps.newHashMap()
    m.put('key1', 'value1')
    m.put('key2', autoclass("java.lang.Integer")(2))
    m.put('key3', autoclass("java.lang.Double")(2.5))

    d = to_dict(m)

    check_dict(d, m)


@istest
def to_map_should_convert_flat_dict():
    d = {'key1': 'value1',
         'key2': 2,
         'key3': 2.5,
         'key4': 'value4',
         3: 'value3',
         4: 5}

    m = to_map(d)

    check_dict(d, m)


def check_dict(d, m):
    for (k, v) in six.iteritems(d):
        if not isinstance(k, six.string_types):
            k = six.u(k)

        if isinstance(v, collections.Mapping):
            check_dict(v, m.get(k))
        else:
            if isinstance(v, six.string_types):
                actual = six.u(m.get(box_number(k)))
                assert_equals(v, actual)
            elif isinstance(v, int) or isinstance(v, float):
                actual = m.get(box_number(k))
                assert_equals(v, actual)
            else:
                actual = m.get(k)
                assert v.equals(actual)


@istest
def to_map_should_convert_nested_dict():
    d = {'key1': 'value1',
         'nested': {'key2': 2,
                    3: 'value3',
                    4: 5}}

    m = to_map(d)

    check_dict(d, m)   
