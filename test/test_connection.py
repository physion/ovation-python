from nose.tools import istest, assert_equal
import urllib.parse
from unittest.mock import Mock, sentinel
import ovation.connection as connection


@istest
def should_set_session_token():
    token = 'my-token'
    s = connection.Session(token)

    assert_equal(s.token, token)


@istest
def should_set_api_base():
    token = 'my-token'
    api_base = 'https://my.server/'
    s = connection.Session(token, api=api_base)

    path = '/some/path'
    assert_equal(s.make_url(path), urllib.parse.urljoin(api_base, path))


@istest
def should_clean_for_update():
    token = 'my-token'
    api_base = 'https://my.server/'
    path = '/api/updates/1'

    response = Mock()
    response.raise_for_status = Mock(return_value=None)
    response.json = Mock(return_value=sentinel.resp)

    s = connection.Session(token, api=api_base)
    s.session.put = Mock(return_value=response)

    entity = {'_id': 1,
              'type': 'Entity',
              'attributes': {'foo': 'bar'},
              'links': {'self': 'url'},
              'owner': 1,
              'relationships': {}}
    expected = {'_id': 1,
                'type': 'Entity',
                'attributes': {'foo': 'bar'}}

    r = s.put(path, entity=entity)
    assert_equal(r, sentinel.resp)
    s.session.put.assert_called_with(urllib.parse.urljoin(api_base, path),
                                     json={'entity': expected})

@istest
def should_proxy_get_requests_session():
    token = 'my-token'
    api_base = 'https://my.server/'
    path = '/api/updates/1'

    response = Mock()
    response.raise_for_status = Mock(return_value=None)
    response.json = Mock(return_value=sentinel.resp)

    s = connection.Session(token, api=api_base)
    s.session.get = Mock(return_value=response)

    assert_equal(s.get(path), sentinel.resp)
