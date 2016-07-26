import uuid
import ovation.contents as contents
import ovation.session as session

from ovation.session import DataDict
from unittest.mock import Mock, sentinel, patch
from nose.tools import istest, assert_equal, set_trace

@istest
@patch('ovation.contents.get_entity_directory_path')
@patch('ovation.contents.get_head_revision')
@patch('ovation.contents.get_contents')
def should_walk_path(get_contents, get_head_revision, get_entity_directory_path):

    project_name = 'proj1'
    file_name = 'file1'
    folder_name = 'folder1'

    get_contents.return_value = {'files': [{'attributes': {'name': file_name }}],
                                 'folders': [{'attributes': {'name': folder_name}}]}
    get_head_revision.return_value = {'attributes': {'name': file_name }}

    get_entity_directory_path.return_value = project_name + "/"

    project = {'attributes': {'name': 'project1'}}

    s = Mock(spec=session.Session)
    recurse = False

    for (parent_path, parent, folders, files, revisions) in contents.walk(s, project):
        assert_equal(parent, project)

        for folder in folders:
            assert_equal(folder['attributes']['name'], 'folder1')

        for file in files:
            assert_equal(file['attributes']['name'], 'file1')
