import pprint

import ovation.session as session
import ovation.lab.results as results

from unittest.mock import sentinel, Mock, patch
from nose.tools import istest


@istest
def should_return_results_for_sample():
    s = Mock(spec=session.Session)
    s.path.return_value = sentinel.workflow_sample_results_path
    s.get.return_value = session.simplify_response({})

    results.get_sample_results(s, sample_id=sentinel.sample_id)

    s.path.assert_called_with('workflow_sample_results', include_org=False)
    s.get.assert_called_with(sentinel.workflow_sample_results_path, params=dict(sample_id=sentinel.sample_id))


@istest
def should_return_results_for_workflow():
    s = Mock(spec=session.Session)
    s.path.return_value = sentinel.workflow_sample_results_path
    s.get.return_value = session.simplify_response({})

    results.get_sample_results(s, workflow_id=sentinel.workflow_id)

    s.path.assert_called_with('workflow_sample_results', include_org=False)
    s.get.assert_called_with(sentinel.workflow_sample_results_path, params=dict(workflow_id=sentinel.workflow_id))


@istest
def should_return_results_for_sample_and_result_type():
    s = Mock(spec=session.Session)
    s.path.return_value = sentinel.workflow_sample_results_path
    s.get.return_value = session.simplify_response({})

    results.get_sample_results(s, sample_id=sentinel.sample_id, result_type=sentinel.result_type)

    s.path.assert_called_with('workflow_sample_results', include_org=False)
    s.get.assert_called_with(sentinel.workflow_sample_results_path,
                             params=dict(sample_id=sentinel.sample_id,
                                         result_type=sentinel.result_type))


@istest
@patch('ovation.lab.resources.get_resource_url')
def should_get_file_urls_from_file_workflow_sample_results(get_resource_url):
    s = Mock(spec=session.Session)

    wsrs = [{'id': 6830,
             'result_type': 'vcf',
             'status': 'accepted',
             'computed_status': None,
             'routing': 'accepted',
             'identifier': sentinel.identifier1,
             'workflow_id': 2418,
             'result': {'file': {'records': [{'filename': 'ngs-clinical-demo-1.vcf',
                                              'sample_id': 'ngs-clinical-demo-1',
                                              'resource_id': sentinel.resource_id1}],
                                 'status': 'unknown',
                                 'reviewed': True}},
             'workflow_sample_id': 8393,
             'global_messages': None,
             'requisition': {'id': 2797, 'accession_status': 'signed'},
             'reviewed': True},
            {'id': 6833,
             'result_type': 'vcf',
             'status': 'accepted',
             'computed_status': None,
             'routing': 'accepted',
             'identifier': sentinel.identifier2,
             'workflow_id': 2418,
             'result': {'file': {'records': [{'filename': 'ngs-clinical-demo-2.vcf',
                                              'sample_id': 'ngs-clinical-demo-2',
                                              'resource_id': sentinel.resource_id2}],
                                 'status': 'unknown'}},
             'workflow_sample_id': 8394,
             'global_messages': None,
             'requisition': {'id': 2798, 'accession_status': 'complete'},
             'reviewed': False}]

    url1 = {'url': sentinel.url1,
            'etag': sentinel.etag1}
    url2 = {'url': sentinel.url2,
            'etag': sentinel.etag2}

    get_resource_url.side_effect = [url1, url2]

    actual = results.get_file_urls(s, wsrs)

    assert actual == {sentinel.identifier1: [url1],
                      sentinel.identifier2: [url2]}


@istest
@patch('ovation.lab.resources.get_resource_url')
def should_get_file_urls_from_file_workflow_sample_results_with_alternate_assay(get_resource_url):
    s = Mock(spec=session.Session)

    assay = sentinel.assay
    wsrs = [{'id': 6830,
             'result_type': 'vcf',
             'status': 'accepted',
             'computed_status': None,
             'routing': 'accepted',
             'identifier': sentinel.identifier1,
             'workflow_id': 2418,
             'result': {assay: {'records': [{'filename': 'ngs-clinical-demo-1.vcf',
                                             'sample_id': 'ngs-clinical-demo-1',
                                             'resource_id': sentinel.resource_id1}],
                                'status': 'unknown',
                                'reviewed': True}},
             'workflow_sample_id': 8393,
             'global_messages': None,
             'requisition': {'id': 2797, 'accession_status': 'signed'},
             'reviewed': True},
            {'id': 6833,
             'result_type': 'vcf',
             'status': 'accepted',
             'computed_status': None,
             'routing': 'accepted',
             'identifier': sentinel.identifier2,
             'workflow_id': 2418,
             'result': {assay: {'records': [{'filename': 'ngs-clinical-demo-2.vcf',
                                             'sample_id': 'ngs-clinical-demo-2',
                                             'resource_id': sentinel.resource_id2}],
                                'status': 'unknown'}},
             'workflow_sample_id': 8394,
             'global_messages': None,
             'requisition': {'id': 2798, 'accession_status': 'complete'},
             'reviewed': False}]

    url1 = {'url': sentinel.url1,
            'etag': sentinel.etag1}
    url2 = {'url': sentinel.url2,
            'etag': sentinel.etag2}

    get_resource_url.side_effect = [url1, url2]

    actual = results.get_file_urls(s, wsrs, assay=assay)

    assert actual == {sentinel.identifier1: [url1],
                      sentinel.identifier2: [url2]}
