import ovation.lab.workflows as workflows

from ovation.session import DataDict,Session,simplify_response
from unittest.mock import Mock, sentinel, patch
from nose.tools import istest, assert_equal
from tqdm import tqdm


@istest
def should_create_activity():
    label = 'activity-label'
    workflow_id = 1
    workflow = {'relationships': {label: {'self': sentinel.activity_url}}}

    s = Mock(spec=Session)
    s.path.return_value = sentinel.workflow_path
    s.get.return_value = simplify_response({'workflow': workflow, 'resources': []})
    s.post.return_value = DataDict({'activity': sentinel.activity})

    activity = {}
    workflows.create_activity(s, workflow_id, label, activity=activity)

    s.path.assert_called_with('workflows', workflow_id)
    s.get.assert_called_with(sentinel.workflow_path)
    s.post.assert_called_with(sentinel.activity_url, data={'activity': activity})


@istest
@patch('ovation.lab.workflows.upload.upload_resource')
def should_create_activity_with_resources(upload):
    label = 'activity-label'
    workflow_id = 1
    workflow = {'relationships': {label: {'self': sentinel.activity_url}}}

    s = Mock(spec=Session)
    s.path.return_value = sentinel.workflow_path
    s.get.return_value = simplify_response({'workflow': workflow, 'resources': []})
    uuid = 'activity-uuid'
    s.post.return_value = DataDict({'activity': {'uuid': uuid}})

    activity = {}
    workflows.create_activity(s, workflow_id, label, activity=activity, resources={'foo': ['foo.txt']})

    s.path.assert_called_with('workflows', workflow_id)
    s.get.assert_called_with(sentinel.workflow_path)
    s.post.assert_called_with(sentinel.activity_url, data={'activity': {'complete': False}})
    upload.assert_called_with(s, uuid, 'foo.txt', label='foo', progress=tqdm)


@istest
@patch('ovation.lab.workflows.upload.upload_resource')
def should_add_custom_attributes_if_needed(upload):
    label = 'activity-label'
    workflow_id = 1
    workflow = {'relationships': {label: {'self': sentinel.activity_url}}}

    s = Mock(spec=Session)
    s.path.return_value = sentinel.workflow_path
    s.get.return_value = simplify_response({'workflow': workflow, 'resources': []})
    uuid = 'activity-uuid'
    s.post.return_value = DataDict({'activity': {'uuid': uuid}})

    activity = {
        'foo': 'bar'
    }
    workflows.create_activity(s, workflow_id, label, activity=activity, resources={'foo': ['foo.txt']})

    s.path.assert_called_with('workflows', workflow_id)
    s.get.assert_called_with(sentinel.workflow_path)
    s.post.assert_called_with(sentinel.activity_url, data={'activity': {'complete': False,
                                                                        'custom_attributes': activity}})
    upload.assert_called_with(s, uuid, 'foo.txt', label='foo', progress=tqdm)


@istest
@patch('ovation.lab.workflows.upload.upload_resource')
def should_handle_existing_custom_attributes(upload):
    label = 'activity-label'
    workflow_id = 1
    workflow = {'relationships': {label: {'self': sentinel.activity_url}}}

    s = Mock(spec=Session)
    s.path.return_value = sentinel.workflow_path
    s.get.return_value = simplify_response({'workflow': workflow, 'resources': []})
    uuid = 'activity-uuid'
    s.post.return_value = DataDict({'activity': {'uuid': uuid}})

    activity = {
        'foo': 'bar',
        'custom_attributes': {'bar': 'baz'}
    }
    workflows.create_activity(s, workflow_id, label, activity=activity, resources={'foo': ['foo.txt']})

    s.path.assert_called_with('workflows', workflow_id)
    s.get.assert_called_with(sentinel.workflow_path)
    s.post.assert_called_with(sentinel.activity_url, data={'activity': {'complete': False,
                                                                        'foo': 'bar',
                                                                        'custom_attributes': {'bar': 'baz'}}})
    upload.assert_called_with(s, uuid, 'foo.txt', label='foo', progress=tqdm)


@istest
def should_get_workflow_samples():
    workflow_id = 1
    s = Mock(spec=Session)
    s.path.return_value = sentinel.workflow_path
    s.get.return_value = {'workflow': {}, 'resources': [], 'samples': [{'type': 'Sample'}]}
    assert_equal(workflows.get_samples(s, workflow_id), [{'type': 'Sample'}])

@istest
def should_get_workflow():
    workflow_id = 1
    s = Mock(spec=Session)
    s.path.return_value = sentinel.workflow_path
    s.get.return_value = {'workflow': sentinel.workflow}

    assert_equal(workflows.get_workflow(s, workflow_id), sentinel.workflow)
