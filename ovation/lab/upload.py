import six
import os

import ovation.upload as upload

from tqdm import tqdm


def _create_resource_group(session, activity, name, parent=None):
    body = {"resource_group": {
        "name": name,
        "activity_id": activity
    }}

    if parent is not None:
        body['resource_group']['parent_id'] = parent

    return session.post(session.entity_path('resource_groups'), data=body)


def upload_resource(session, entity_id, local_path, label=None, resource_group=None, progress=tqdm):
    """
    Upload a single local file as a Resource

    :param session: Session
    :param entity_id: owning entity UUID
    :param local_path: local file path
    :param label: Resource label
    :param resource_group: (optional) ResourceGroup dict
    :param progress: (optional) progress monitor
    :return: new Resource dict
    """

    file_name = os.path.basename(local_path)
    content_type = upload.guess_content_type(file_name)

    data = {'resource': {'entity_id': entity_id,
                         'path': file_name}}
    if label:
        data['resource']['label'] = label

    if resource_group is not None:
        data['resource']['resource_group_id'] = resource_group.id

    r = session.post(session.entity_path('resources'), data=data)
    aws = r['aws']

    upload.upload_to_aws(aws, content_type, local_path, progress)

    metadata = session.get(session.entity_path('resources', r.id) + "/metadata")

    r.version = metadata.version_id
    r.type = 'resource'

    return session.put(session.entity_path('resources', r.id), entity=r)


def upload_resource_group(session, activity, local_directory_path, label=None, progress=tqdm):
    """
    Recursively uploads a folder to Ovation as a ResourceGroup

    :param session: Session
    :param local_directory_path: local path to directory
    :param activity: activity UUID or dict
    :param label: Resources' label
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    """

    if not isinstance(activity, six.string_types):
        activity = activity['uuid']

    parent_id = None
    root_group = None
    for root, dirs, files in os.walk(local_directory_path):
        root_name = os.path.basename(root)
        if len(root_name) == 0:
            root_name = os.path.basename(os.path.dirname(root))

        resource_group = _create_resource_group(session, activity, root_name, parent=parent_id)
        if root_group is None:
            root_group = resource_group
        parent_id = resource_group.id

        for f in files:
            path = os.path.join(root, f)

            upload_resource(session, activity, path, label=label, resource_group=resource_group, progress=progress)

    return root_group


def upload_resources(session, activity, resources, progress=tqdm):
    """
    Uploads a resources collection to an activity.

    :param session:  ovation.session.Session
    :param activity: activity UUID string or dict
    :param resources: local path(s) to activity Resources (by label)
    """

    if not isinstance(activity, six.string_types):
        activity = activity['uuid']

    for (label, paths) in six.iteritems(resources):
        for local_path in paths:
            upload_resource(session, activity, local_path, label=label, progress=progress)
