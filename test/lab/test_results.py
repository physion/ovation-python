import ovation.session as session
import ovation.lab.results as results

from unittest.mock import sentinel, Mock, patch
from nose.tools import istest, assert_is_not_none


@istest
def should_return_results_for_sample():
    s = Mock(spec=session.Session)
    s.path.return_value = sentinel.workflow_sample_results_path
    s.get.return_value = session.simplify_response({})

    results.get_results(s, sample_id=sentinel.sample_id)

    s.path.assert_called_with('workflow_sample_results', include_org=False)
    s.get.assert_called_with(sentinel.workflow_sample_results_path, sample_id=sentinel.sample_id)


@istest
def should_return_results_for_workflow():
    s = Mock(spec=session.Session)
    s.path.return_value = sentinel.workflow_sample_results_path
    s.get.return_value = session.simplify_response({})

    results.get_results(s, workflow_id=sentinel.workflow_id)

    s.path.assert_called_with('workflow_sample_results', include_org=False)
    s.get.assert_called_with(sentinel.workflow_sample_results_path, workflow_id=sentinel.workflow_id)


@istest
def should_return_results_for_sample_and_result_type():
    s = Mock(spec=session.Session)
    s.path.return_value = sentinel.workflow_sample_results_path
    s.get.return_value = session.simplify_response({})

    results.get_results(s, sample_id=sentinel.sample_id, result_type=sentinel.result_type)

    s.path.assert_called_with('workflow_sample_results', include_org=False)
    s.get.assert_called_with(sentinel.workflow_sample_results_path,
                             sample_id=sentinel.sample_id,
                             result_type=sentinel.result_type)
