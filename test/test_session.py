import requests.exceptions
from nose.tools import istest, assert_equal
from six.moves.urllib_parse import urljoin
from unittest.mock import Mock, sentinel, patch
import ovation.session as session
import json


@istest
def should_set_session_token():
    token = 'my-token'
    s = session.Session(token)

    assert_equal(s.token, token)


@istest
def should_set_api_base():
    token = 'my-token'
    api_base = 'https://my.server/'
    s = session.Session(token, api=api_base)

    path = '/api/v1/some/path'
    assert_equal(s.make_url(path), urljoin(api_base, path))

@istest
def should_add_prefix():
    token = 'my-token'
    api_base = 'https://my.server/'
    s = session.Session(token, api=api_base)

    path = '/some/path'
    assert_equal(s.make_url(path), urljoin(api_base, '/api/v1' + path))

@istest
def should_remove_double_slashes_in_url():
    token = 'my-token'
    api_base = 'https://my.server/'
    s = session.Session(token, api=api_base)

    path = '/some//path'
    assert_equal(s.make_url(path), urljoin(api_base, ('/api/v1' + path).replace('//','/')))


@istest
def should_make_type_index_url():
    s = session.Session(sentinel.token)

    assert_equal(s.path('project', include_org=False), '/projects/')


@istest
def should_make_type_index_url_with_default_org():
    s = session.Session(sentinel.token)

    assert_equal(s.path('project'), '/o/0/projects/')


@istest
def should_make_type_index_url_with_org():
    s = session.Session(sentinel.token)

    assert_equal(s.path('project', org=123), '/o/123/projects/')


@istest
def should_make_type_get_url():
    s = session.Session(sentinel.token)

    assert_equal(s.path('project', entity_id='123', include_org=False), '/projects/123')

@istest
def should_make_type_get_url_with_default_org():
    s = session.Session(sentinel.token)

    assert_equal(s.path('project', entity_id='123'), '/o/0/projects/123')


@istest
def should_make_type_get_url_with_org():
    s = session.Session(sentinel.token)

    assert_equal(s.path('project', entity_id='123', org=235), '/o/235/projects/123')


@istest
def should_exclude_org_if_none():
    s = session.Session(sentinel.token, org=None)

    assert_equal(s.path('workflows', entity_id='123'), '/workflows/123')


@istest
def should_return_single_entry_value():
    s = session


    entities = ['foo', 'bar']
    assert_equal(s.simplify_response({'entities': entities}), entities)


@istest
def should_return_datadict():
    s = session
    result = s.simplify_response({'bar': 'baz',
                                  'foo': sentinel.bar})

    assert_equal(result.bar, 'baz')


@istest
def should_return_multientry_keys_and_values():
    s = session

    d = {'entities': sentinel.entities,
         'others': 'foo'}
    assert_equal(s.simplify_response(d), d)

@istest
def should_simplify_tags_response():
    s = session
    d = {
        "tags": [
            {
                "_id": "b1a268af-3bf1-4a13-a530-68e9cc4b9367",
                "user": "5162ef4f-8c57-4c2c-8e35-2a3f4f114275",
                "entity": "f2bfa3da-7eae-45c4-80a5-9e9a3588a237",
                "annotation_type": "tags",
                "annotation": {
                    "tag": "mytag"
                },
                "type": "Annotation",
                "links": {
                    "_collaboration_roots": [
                        "f2bfa3da-7eae-45c4-80a5-9e9a3588a237"
                    ]
                },
                "permissions": {
                    "update": True,
                    "delete": True
                }
            }
        ]
    }

    expected = [
            {
                "_id": "b1a268af-3bf1-4a13-a530-68e9cc4b9367",
                "user": "5162ef4f-8c57-4c2c-8e35-2a3f4f114275",
                "entity": "f2bfa3da-7eae-45c4-80a5-9e9a3588a237",
                "annotation_type": "tags",
                "annotation": {
                    "tag": "mytag"
                },
                "type": "Annotation",
                "links": {
                    "_collaboration_roots": [
                        "f2bfa3da-7eae-45c4-80a5-9e9a3588a237"
                    ]
                },
                "permissions": {
                    "update": True,
                    "delete": True
                }
            }
        ]

    assert_equal(s.simplify_response(d), expected)


@istest
def should_clean_for_update():
    token = 'my-token'
    api_base = 'https://my.server/'
    path = '/api/v1/updates/1'

    response = Mock()
    response.raise_for_status = Mock(return_value=None)
    response.json = Mock(return_value=sentinel.resp)

    s = session.Session(token, api=api_base)
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
    s.session.put.assert_called_with(urljoin(api_base, path),
                                     json={'entity': expected})

@istest
def should_proxy_get_requests_session():
    token = 'my-token'
    api_base = 'https://my.server/'
    path = '/api/updates/1'

    response = Mock()
    response.raise_for_status = Mock(return_value=None)
    response.json = Mock(return_value=sentinel.resp)

    s = session.Session(token, api=api_base)
    s.session.get = Mock(return_value=response)

    assert_equal(s.get(path), sentinel.resp)


@istest
def should_retry_failed_requests():
    token = 'my-token'
    api_base = 'https://my.server/'
    path = '/api/updates/1'

    response = Mock()
    response.raise_for_status = Mock(return_value=None)
    response.json = Mock(return_value=sentinel.resp)

    s = session.Session(token, api=api_base, retry=1)
    s.session.get = Mock(side_effect=[requests.exceptions.HTTPError(), response])

    assert_equal(s.get(path), sentinel.resp)


@istest
@patch('ovation.session.read_saved_token')
def should_use_saved_token(rst):
    rst.return_value = sentinel.token

    assert_equal(session.connect(sentinel.email).token, sentinel.token)
    rst.assert_called_with(sentinel.email, url=session.DEFAULT_HOST)


@istest
def should_generate_json():
    s = session.Session('TOKEN', api='API', prefix='PREFIX', retry=1)

    assert_equal(json.dumps({'token': 'TOKEN',
                             'api_base': 'API',
                             'prefix': 'PREFIX',
                             'retry': 1}),
                 s.json())


@istest
def should_build_from_json():
    json_session = json.dumps({'token': 'TOKEN',
                               'api_base': 'API',
                               'prefix': 'PREFIX',
                               'retry': 1})

    s = session.Session.from_json(json_session)

    assert_equal(s.json(), json_session)
