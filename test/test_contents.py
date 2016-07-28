import uuid
import ovation.contents as contents
import ovation.session as session

from ovation.session import DataDict
from unittest.mock import Mock, sentinel, patch
from nose.tools import istest, assert_equal, set_trace

@istest
@patch('ovation.contents.get_breadcrumbs')
@patch('ovation.contents.get_head_revision')
@patch('ovation.contents.get_contents')
def should_walk_path(get_contents, get_head_revision, get_breadcrumbs):

    project_name = 'proj1'
    file_name = 'file1'
    folder_name = 'folder1'

    get_contents.return_value = {'files': [{'attributes': {'name': file_name }}],
                                 'folders': [{'attributes': {'name': folder_name}}]}
    get_head_revision.return_value = {'attributes': {'name': file_name }}

    get_breadcrumbs.return_value = project_name + "/"

    project = {'attributes': {'name': project_name}}

    s = Mock(spec=session.Session)

    for (parent, folders, files) in contents.walk(s, project):
        assert_equal(parent, project)

        for folder in folders:
            assert_equal(folder['attributes']['name'], folder_name)

        for file in files:
            assert_equal(file['attributes']['name'], file_name)
