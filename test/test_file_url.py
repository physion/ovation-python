from nose.tools import istest

from ovation.core import File
from ovation.conversion import to_file_url


@istest
def should_convert_local_path_to_url():
    path = "abc/def"
    expected = File(path).toURI().toURL()
    assert(expected.equals(to_file_url(path)))

