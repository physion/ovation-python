import os.path

import requests
import six
from tqdm import __init__


def revision_download_info(session, revision):
    """
    Get temporary download link and ETag for a Revision.

    :param session: ovation.connection.Session
    :param revision: revision entity dictionary or revision ID string
    :return: dict with `url`, `etag`, and S3 `path`
    """

    if isinstance(revision, six.string_types):
        e = session.get(session.make_type_path('entities', id=revision))
        if e.type == 'Revision':
            revision = e
        else:
            revision = session.get(e.links.heads)[0]

    if revision['type'] == 'File':
        revision = session.get(e.links.heads)[0]

    r = session.session.get(revision['attributes']['url'],
                            headers={'accept': 'application/json'},
                            params={'token': session.token})
    r.raise_for_status()

    return r.json()


def download_revision(session, revision, output=None):
    """
    Downloads a Revision to the local file system. If output is provided, file is downloaded
    to the output path. Otherwise, it is downloaded to the current working directory.

    If a File (entity or ID) is provided, the HEAD revision is downloaded.

    :param session: ovation.connection.Session
    :param revision: revision entity dictionary or ID string, or file entity dictionary or ID string
    :param output: path to folder to save downloaded revision
    :return: file path
    """

    url = revision_download_info(session, revision)['url']
    response = requests.get(url, stream=True)

    name = os.path.basename(urlsplit(url).path)
    if output:
        dest = os.path.join(output, name)
    else:
        dest = name

    with open(dest, "wb") as f:
        for data in tqdm(response.iter_content()):
            f.write(data)
