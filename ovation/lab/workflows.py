import six
import os

import ovation.lab.upload as upload

from tqdm import tqdm


def create_activity(session, workflow_id, activity_label, data={},
                    resources={}, resource_groups={},
                    progress=tqdm):
    """
    Creates a new workflow activity

    :param session: ovation.session.Session
    :param workflow_id: workflow ID
    :param activity_label: activity label
    :param data: activity metadata
    :param resources: local path(s) to activity Resources (by label)
    :param resource_groups: local path(s) to activity ResourceGroups (by label)
    :return: newly created Activity dict
    """
    workflow = session.get(session.entity_path('workflows', workflow_id))
    activity_path = workflow.links[activity_label].self

    activity = session.post(activity_path, data=data)

    for (label, paths) in six.iteritems(resources):
        for local_path in paths:
            upload.upload_resource(session, activity.uuid, local_path, label=label, progress=progress)

    for (label, paths) in six.iteritems(resource_groups):
        for local_path in paths:
            upload.upload_resource_group(session, activity, local_path, label=label, progress=progress)

    return activity
