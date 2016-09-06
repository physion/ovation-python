import six
import os
import ovation.download

from tqdm import tqdm

def download_resources(session,
                       workflow,
                       activity_label,
                       resource_label, output=None, progress=tqdm):
    """
    Download the Resources for a labeled activity. Resources with the given label are downloaded
    to the given output directory.

    :param session: ovation.session.Session
    :param workflow: workflow Dict
    :param activity_label: configured activity label (unique within workflow)
    :param resource_label: desired resource_label
    :param output: output directory path
    :param progress: tqdm-like progress indicator

    """

    activity = session.get(workflow.relationships[activity_label].related)

    # Find the activity resources with the given label
    resources = [r for r in activity.activity.resources if r.label == resource_label]

    for r in resources:
        ovation.download.download_url(r.read_url, output=output, progress=progress)


