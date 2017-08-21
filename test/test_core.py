import uuid
import ovation.core as core
import ovation.session as session

from unittest.mock import Mock, sentinel, patch
from nose.tools import istest, assert_equal


@istest
def should_create_file():
    s = Mock(spec=session.Session)
    s.get = Mock()
    s.get.side_effect = [session.DataDict({'type': 'Project',
                                           '_id': make_uuid(),
                                           'links': session.DataDict({'self': sentinel.parent_self})})]
    s.post = Mock()
    file = {'entities': [{'type': 'File',
                          '_id': make_uuid()}]}
    s.post.return_value = file
    expected_name = 'file name'

    core.create_file(s, make_uuid(), expected_name)

    s.post.assert_called_once_with(sentinel.parent_self, data={'entities': [{'type': 'File',
                                                                             'attributes': {'name': expected_name}}]})

@istest
def should_create_folder():
    s = Mock(spec=session.Session)
    s.get = Mock()
    s.get.side_effect = [session.DataDict({'type': 'Project',
                                           '_id': make_uuid(),
                                           'links': session.DataDict({'self': sentinel.parent_self})})]
    s.post = Mock()
    folder = {'entities': [{'type': 'Folder',
            '_id': make_uuid()}]}

    s.post.return_value = folder
    expected_name = 'folder name'


    core.create_folder(s, make_uuid(), expected_name)

    s.post.assert_called_once_with(sentinel.parent_self, data={'entities': [{'type': 'Folder',
                                                                             'attributes': {'name': expected_name}}]})


def make_uuid():
    return str(uuid.uuid4())


@istest
def should_trash_entity_by_id():
    s = Mock(spec=session.Session)

    s.delete.return_value = sentinel.deleted
    s.path.return_value = sentinel.path

    id = 'entity-id'
    r = core.delete_entity(s, id)

    s.delete.assert_called_once_with(sentinel.path)

@istest
def should_trash_entity():
    s = Mock(spec=session.Session)

    s.delete.return_value = sentinel.deleted
    s.path.return_value = sentinel.path

    id = 'entity-id'
    r = core.delete_entity(s, {"_id": id})

    s.delete.assert_called_once_with(sentinel.path)


@istest
def should_undelete_entity():
    entity_id = make_uuid()

    s = Mock(spec=session.Session)
    s.get.return_value = session.DataDict({'_id': entity_id,
                                           'trash_info': sentinel.trash_info})
    s.put.return_value = session.DataDict({'_id': entity_id})
    s.path.return_value = "/api/v1/entities/{}".format(entity_id)

    core.undelete_entity(s, entity_id)

    s.get.assert_called_once_with(s.path.return_value, params={'trash': "true"})
    s.put.assert_called_once_with(s.path.return_value + "/restore", s.get.return_value)



@istest
def should_get_entity():
    s = Mock(spec=session.Session)
    s.get.return_value = sentinel.result
    s.path.return_value = sentinel.path

    core.get_entity(s, 'entity-id')

    s.get.assert_called_once_with(sentinel.path, params={'trash': "false"})

@istest
def should_return_existing_entity_dict():

    assert_equal(core.get_entity(sentinel.session, sentinel.entity_dict),
                 sentinel.entity_dict)


@istest
def should_add_link():
    entity = {'relationships': {'foo': {'self': 'self-url'}}}
    rel_url = 'self-url'

    s = Mock(spec=session.Session)
    s.post.return_value = sentinel.result

    expected_post = [{'target_id': sentinel.target,
                      'inverse_rel': sentinel.inverse_rel}]

    core.add_link(s, entity, target=sentinel.target, rel='foo', inverse_rel=sentinel.inverse_rel)

    s.post.assert_called_once_with(rel_url, data=expected_post)


@istest
def should_remove_link():
    entity = {'_id': sentinel.entity_id,
              'relationships': {'foo': {'self': 'self-url'}},
              'organization_id': sentinel.org}
    rel_url = 'self-url'

    s = Mock(spec=session.Session)
    s.get.return_value = [{'_id': sentinel.link_id,
                           'target_id': sentinel.target,
                           'inverse_rel': sentinel.inverse_rel},
                          {'target_id': sentinel.target2,
                           'inverse_rel': sentinel.inverse_rel2}]
    s.delete.return_value = sentinel.result
    s.path.return_value = sentinel.url

    core.remove_link(s, entity, target=sentinel.target, rel='foo')

    s.get.assert_called_once_with(rel_url)
    s.path.assert_called_with('relationships', entity_id=sentinel.link_id, org=sentinel.org)
    s.delete.assert_called_once_with(sentinel.url)
