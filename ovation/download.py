import os.path

import requests
import six

from tqdm import tqdm
from six.moves.urllib_parse import urlsplit


def revision_download_info(session, revision):
    """
    Get temporary download link and ETag for a Revision.

    :param session: ovation.connection.Session
    :param revision: revision entity dictionary or revision ID string
    :return: dict with `url`, `etag`, and S3 `path`
    """

    if isinstance(revision, six.string_types):
        e = session.get(session.entity_path('entities', id=revision))
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


def download_revision(session, revision, output=None, progress=tqdm):
    """
    Downloads a Revision to the local file system. If output is provided, file is downloaded
    to the output path. Otherwise, it is downloaded to the current working directory.

    If a File (entity or ID) is provided, the HEAD revision is downloaded.

    :param session: ovation.connection.Session
    :param revision: revision entity dictionary or ID string, or file entity dictionary or ID string
    :param output: path to folder to save downloaded revision
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
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
        if progress:
            for data in progress(response.iter_content(),
                                 unit='B',
                                 unit_scale=True,
                                 miniters=1):
                f.write(data)
        else:
            for data in response.iter_content():
                f.write(data)
