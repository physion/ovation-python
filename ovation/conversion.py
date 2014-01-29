import collections
import numbers

from ovation import Maps, Sets, cast, autoclass, Integer, Double, File, DateTime, DateTimeZone


class Iterator(object):
    def __init__(self, jiterator):
        self.java_iterator = jiterator

    def __iter__(self):
        return self

    def next(self):
        if (self.java_iterator.hasNext()):
            return self.java_iterator.next()

        raise StopIteration()


class IterableWrapper(object):
    def __init__(self, jiterable):
        self.java_iterable = jiterable

    def __iter__(self):
        return Iterator(self.java_iterable.iterator())


def iterable(java_iterable):
    return IterableWrapper(java_iterable)


def to_java_datetime(d):
    tz = DateTimeZone.forID(d.tzinfo.tzname(d))
    return DateTime(d.year, 
                    d.month, 
                    d.day, 
                    d.hour, 
                    d.minute, 
                    d.second, 
                    d.microsecond/1000, 
                    tz)

def to_map(d):
    result = Maps.newHashMap()
    for (k, v) in d.iteritems():
        if not isinstance(k, basestring):
            k = unicode(k)
        if isinstance(v, collections.Mapping):
            nested_value = to_map(v)
            result.put(k, nested_value)
        else:
            result.put(k, box_number(v))

    return result


def to_dict(m):
    result = {}
    for k in m.keySet().toArray():
        result[k] = m.get(k)

    return result
    #return {key: m.get(key) for key in iterable(m.keySet())}


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

def to_java_set(s):
    result = Sets.newHashSet()
    for item in s:
        result.add(box_number(item))

    return result



def asclass(cls_name, o):
    if o is None:
        return o

    if len(cls_name.split('.')) == 1:
        cls_name = "us.physion.ovation.domain.{}".format(cls_name)

    return cast(autoclass(cls_name), o)

