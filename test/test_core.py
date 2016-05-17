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
