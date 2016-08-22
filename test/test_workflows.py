import ovation.lab.workflows as workflows

from ovation.session import DataDict,Session,simplify_response
from unittest.mock import Mock, sentinel, patch
from nose.tools import istest, assert_equal


@istest
def should_create_activity():
    label = 'activity-label'
    workflow_id = 1
    workflow = {'relationships': {label: {'self': sentinel.activity_url}}}

    s = Mock(spec=Session)
    s.entity_path.return_value = sentinel.workflow_path
    s.get.return_value = simplify_response({'workflow': workflow, 'resources': []})
    s.post.return_value = sentinel.activity

    workflows.create_activity(s, workflow_id, label, activity=sentinel.data)

    s.entity_path.assert_called_with('workflows', workflow_id)
    s.get.assert_called_with(sentinel.workflow_path)
    s.post.assert_called_with(sentinel.activity_url, data=sentinel.data)
