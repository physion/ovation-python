import collections
import numbers
import six

from ovation import cast, autoclass
from ovation.core import Maps, Sets, Integer, Double, File, DateTime, DateTimeZone


def asclass(cls_name, o):
    if o is None:
        return o

    if len(cls_name.split('.')) == 1:
        cls_name = "us.physion.ovation.domain.{}".format(cls_name)

    return cast(autoclass(cls_name), o)

def datetime(d):
    tz = DateTimeZone.forID(d.tzinfo.zone)
    return DateTime(d.year, 
                    d.month, 
                    d.day, 
                    d.hour, 
                    d.minute, 
                    d.second, 
                    d.microsecond/1000, 
                    tz)

def to_java_datetime(d):
    return datetime(d)

def to_map(d):
    result = Maps.newHashMap()
    for (k, v) in six.iteritems(d):
        if not isinstance(k, six.string_types):
            k = six.u(k)
        if isinstance(v, collections.Mapping):
            nested_value = to_map(v)
            result.put(k, nested_value)
        else:
            result.put(box_number(k), box_number(v))

    return result


def to_dict(m):
    result = {}
    for k in m.keySet().toArray():
        result[k] = m.get(k)

    return result


def box_number(item):
    """Boxes a Python number as a Java number object"""

    if isinstance(item, numbers.Number):
        if isinstance(item, numbers.Integral):
            value = Integer(item)
        else:
            value = Double(item)
    else:
        value = item
    return value


def to_file_url(path):
    """
    Constructs a java.net.URL from a file system path

    Arguments
    ---------
    path : string
        file system path

    Returns
    -------
    url : java.net.URL
        file URL
    """

    return File(path).toURI().toURL()



def to_set(s):
    result = Sets.newHashSet()
    for item in s:
        result.add(box_number(item))

    return result


def to_java_set(s):
    return to_set(s)



