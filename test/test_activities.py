from unittest.mock import sentinel, Mock, patch
from nose.tools import istest, assert_is_not_none

import ovation.activities as activities
import ovation.session as session
import ovation.core as core


@istest
@patch('ovation.session.simplify_response')
@patch('ovation.upload.upload_file')
@patch('os.path.isfile')
def should_create_activity(isfile, upload_file, simplify_response):
    revision = {'type': 'Revision',
                '_id': sentinel.revision_id}
    source = {'type': 'Source',
              '_id': sentinel.source_id}

    proj = {'type': 'Project',
            '_id': sentinel.project_id,
            'links': {'self': sentinel.project_self}}

    output_revision = {'type': core.REVISION_TYPE,
                       '_id': sentinel.output_revision_id}

    s = Mock(spec=session.Session)
    post_activity_return = {'type': core.ACTIVITY_TYPE}
    s.post.return_value = {'activities': [post_activity_return]}
    simplify_response.return_value = sentinel.activity
    s.path.return_value = sentinel.activities_url

    output_path = '/some/path.txt'
    isfile.return_value = True
    upload_file.return_value = output_revision

    expected_post = {'type': core.ACTIVITY_TYPE,
                     'attributes': {'name': sentinel.activity_name},
                     'relationships': {'parents': {'related': [proj['_id']],
                                                   'type': core.PROJECT_TYPE,
                                                   'inverse_rel': 'activities',
                                                   'create_as_inverse': True},
                                       'inputs': {'related': [input['_id'] for input in [revision, source]],
                                                  'type': core.REVISION_TYPE,
                                                  'inverse_rel': 'activities'},
                                       'outputs': {'related': [output['_id'] for output in [output_revision]],
                                                  'type': core.REVISION_TYPE,
                                                  'inverse_rel': 'origins'},
                                       'actions': {'related': [r['_id'] for r in []],
                                                   'type': core.REVISION_TYPE,
                                                   'inverse_rel': 'procedures'}}}

    activity = activities.create_activity(s, proj, sentinel.activity_name,
                                          inputs=[revision, source],
                                          outputs=[output_path])

    assert_is_not_none(activity)
    upload_file.assert_called_with(s, proj, output_path)
    s.post.assert_called_with(sentinel.activities_url, data={'activities': [expected_post]})
    simplify_response.assert_called_once_with(post_activity_return)
