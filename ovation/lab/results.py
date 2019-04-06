from typing import Dict, Iterable

import ovation.session
import ovation.lab.resources as resources
import ovation.lab.constants as constants

from ovation.lab.constants import WORKFLOW_SAMPLE_RESULTS, WSR_RESULT_RECORDS_KEY, WSR_RESULT_KEY


def get_sample_results(session: ovation.session.Session,
                       sample_id: int = None,
                       result_type: str = None,
                       workflow_id: int =None) -> Iterable[Dict]:
    params = {}
    if sample_id:
        params['sample_id'] = sample_id

    if result_type:
        params['result_type'] = result_type

    if workflow_id:
        params['workflow_id'] = workflow_id

    return session.get(session.path(WORKFLOW_SAMPLE_RESULTS, include_org=False),
                       params=params)


def get_file_urls(session: ovation.session.Session,
                  results: Iterable[Dict],
                  assay: str = constants.FILE_ASSAY) -> Dict[str, Iterable[Dict[str,str]]]:
    """
    Get temporary download URLs for the resources associated with the iterable of results
    :param session: ovation.session.Session
    :param results: iterable of WorkflowSampleResults Dict
    :param assay: WorkflowSampleResult assay (default: 'file')
    :return: map of URLs {sample.identifier => [{url,etag}]}
    """

    urls = {}
    for sample_result in results:
        identifier = sample_result.get('identifier', 'unknown')
        sample_urls = urls.get(identifier, [])
        records = sample_result.get(WSR_RESULT_KEY, {}).get(assay, {}).get(WSR_RESULT_RECORDS_KEY, [])

        for record in records:
            resource_id = record.get('resource_id')
            sample_urls.append(resources.get_resource_url(session, resource_id))

        urls[identifier] = sample_urls

    return urls
