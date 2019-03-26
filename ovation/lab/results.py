from ovation.lab.constants import WORKFLOW_SAMPLE_RESULTS


def get_results(session, sample_id=None, result_type=None, workflow_id=None):
    params = {}
    if sample_id:
        params['sample_id'] = sample_id

    if result_type:
        params['result_type'] = result_type

    if workflow_id:
        params['workflow_id'] = workflow_id

    return session.get(session.path(WORKFLOW_SAMPLE_RESULTS, include_org=False),
                       **params)
