import ovation.session as session
import ovation.lab.resources as resources

from unittest.mock import sentinel, Mock
from nose.tools import istest


@istest
def should_get_resource_url():
    s = Mock(spec=session.Session)
    resource_id = sentinel.resource_id

    response = {'url': sentinel.url,
                'etag': sentinel.etag,
                'path': sentinel.path}

    s.get.return_value = response
    s.path.return_value = sentinel.resource_path

    actual = resources.get_resource_url(s, resource_id)

    s.path.assert_called_with('resources', resource_id)
    s.get.assert_called_with(sentinel.resource_path)
    assert actual == {'url': sentinel.url, 'etag': sentinel.etag}

