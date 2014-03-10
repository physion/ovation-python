import json
import requests
from nose.tools import istest, assert_equals, assert_true, assert_raises
from requests.exceptions import ConnectionError
from ovation.web import WebApi, _join
from mock import MagicMock, patch, sentinel, ANY


@istest
def should_have_endpoint():
    api = WebApi('username', 'password')
    assert_equals('https://ovation.io/api/v1/', api.api_endpoint())


@istest
@patch('requests.post')
def should_get_api_key(mock_post):
    expected_key = _setup_mock_sessions_post(mock_post)

    api = WebApi(sentinel.email, sentinel.password)
    key = api.api_key()

    auth_data = {'email' : sentinel.email, 'password' : sentinel.password}
    mock_post.assert_called_once_with(_join(api.api_endpoint(), 'sessions'), data=auth_data)
    assert_equals(expected_key, key)


def _setup_mock_sessions_post(mock_post):
    expected_key = 'my-api-key'
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'api_key': expected_key}

    return expected_key


@istest
@patch('requests.post')
def should_authenticate_once(mock_post):
    _setup_mock_sessions_post(mock_post)

    api = WebApi(sentinel.email, sentinel.password)
    api.api_key()
    api.api_key()

    mock_post.assert_called_once_with(_join(api.api_endpoint(), 'sessions'), data=ANY)


@istest
@patch('requests.post')
@patch('requests.get')
def should_get_jar_info(mock_get, mock_post):
    _setup_mock_sessions_post(mock_post)

    tag = '123abc'
    url = 'https://cloud.com/123'

    mock_get.return_value.status_code = 200
    expected_result = {'etag': tag, 'url': url}
    mock_get.return_value.json.return_value = expected_result

    api = WebApi(sentinel.email, sentinel.password)
    result = api.jar_info()

    assert_equals(result, expected_result)

@istest
@patch('requests.post')
@patch('requests.get')
def jar_info_should_raise_connection_error_when_offline(mock_get, mock_post):
    _setup_mock_sessions_post(mock_post)

    mock_get.side_effect = ConnectionError()
    api = WebApi(sentinel.email, sentinel.password)

    assert_raises(ConnectionError, api.jar_info)
