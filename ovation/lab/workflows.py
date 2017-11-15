import six
import os

import ovation.lab.upload as upload

from tqdm import tqdm


def create_activity(session, workflow_id, activity_label, activity=None,
                    resources=None, resource_groups=None,
                    progress=tqdm):
    """
    Creates a new workflow activity.

    :param session: ovation.session.Session
    :param workflow_id: workflow ID
    :param activity_label: activity label
    :param activity: activity record
    :param resources: local path(s) to activity Resources (by label)
    :param resource_groups: local path(s) to activity ResourceGroups (by label)
    :return: newly created Activity dict
    """

    if resource_groups is None:
        resource_groups = {}
    if resources is None:
        resources = {}
    if activity is None:
        activity = {}

    if len(activity.keys()) > 0 and not 'custom_attributes' in activity:
        activity = {'custom_attributes': activity}

    workflow = session.get(session.path('workflows', workflow_id)).workflow
    activity_path = workflow.relationships[activity_label].self

    if len(resources) > 0 or len(resource_groups) > 0:
        activity['complete'] = False

    activity = session.post(activity_path, data={'activity': activity}).activity

    for (label, paths) in six.iteritems(resources):
        for local_path in paths:
            upload.upload_resource(session, activity['uuid'], local_path, label=label, progress=progress)

    for (label, paths) in six.iteritems(resource_groups):
        for local_path in paths:
            upload.upload_resource_group(session, activity, local_path, label=label, progress=progress)

    return activity


def get_activity(session, workflow, label):
    return session.get(workflow.relationships[label].related).activity


def get_workflow(session, workflow):
    return session.get(session.path('workflow'), workflow)['workflow']


def get_samples(session, workflow):
    """
    Gets all samples in a workflow.

    :param session: ovation.session.Session
    :param workflow: workflow Id or Dict
    :return: list of Sample records
    """

    if isinstance(workflow, int):
        wf = session.get(session.path('workflow', workflow))
        return wf['samples']
    else:
        return workflow['samples']
