import os.path

import functools
import requests
import six
import logging
import retrying

import ovation.core as core
import ovation.contents as contents

from tqdm import tqdm
from six.moves.urllib_parse import urlsplit
from pprint import pprint
from multiprocessing.pool import ThreadPool as Pool

DEFAULT_CHUNK_SIZE = 1024 * 1024


class DownloadException(Exception):
    def __init__(self, msg):
        super(DownloadException, self).__init__(msg)


def revision_download_info(session, file_or_revision):
    """
    Get temporary download link and ETag for a Revision.

    :param session: ovation.connection.Session
    :param file_or_revision: revision entity dictionary or revision ID string
    :return: dict with `url`, `etag`, and S3 `path`
    """

    if isinstance(file_or_revision, six.string_types):
        file_or_revision = session.get(session.entity_path('entities', entity_id=file_or_revision))
        if file_or_revision.type not in [core.REVISION_TYPE, core.FILE_TYPE]:
            raise Exception("Whoops! {} is not a File or Revision".format(file_or_revision))

    if file_or_revision['type'] == core.FILE_TYPE:
        revision = contents.get_head_revision(session, file_or_revision)
        if revision is None:
            raise DownloadException("No revisions found for {}".format(file_or_revision._id))
    else:
        revision = file_or_revision

    if not revision['type'] == core.REVISION_TYPE:
        raise Exception("Whoops! {} is not a File or Revision".format(revision['_id']))

    r = session.session.get(revision['attributes']['url'],
                            headers={'accept': 'application/json'},
                            params={'token': session.token})
    r.raise_for_status()

    return r.json()


@retrying.retry(stop_max_attempt_number=3)
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

    info = revision_download_info(session, revision)
    url = info['url']

    download_url(url, progress=progress, output=output)


def download_url(url, output=None, progress=tqdm):
    response = requests.get(url, stream=True)

    name = os.path.basename(urlsplit(url).path)
    if output:
        dest = os.path.join(output, name)
    else:
        dest = name
    with open(dest, "wb") as f:
        if progress:
            for data in progress(response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE),
                                 unit='MB',
                                 unit_scale=True,
                                 miniters=1):
                f.write(data)
        else:
            for data in response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE):
                f.write(data)


def _download_revision_path(session, revision_path, progress=tqdm):
    try:
        return download_revision(session, revision_path[1], output=revision_path[0], progress=progress)
    except DownloadException as e:
        logging.error("Download error: {}".format(e))


def download_folder(session, folder, output=None, progress=tqdm):
    files = _traverse_folder(session, folder, output=output, progress=progress)
    with Pool() as p:
        for f in progress(p.imap_unordered(functools.partial(_download_revision_path,
                                                             session,
                                                             progress=None),
                                           files),
                          desc='Downloading files',
                          unit='file',
                          total=len(files)):
            pass


def _traverse_folder(session, folder, output=None, progress=tqdm):
    folder = core.get_entity(session, folder)
    if folder is None:
        return

    # make folder
    if output is None:
        path = folder.attributes.name
    else:
        path = os.path.join(output, folder.attributes.name)

    if not os.path.isdir(path):
        os.mkdir(path)

    # get files
    files = [[path, f] for f in session.get(folder.relationships.files.related)]

    # for each folders, recurse and return files
    folders = session.get(folder.relationships.folders.related)
    with Pool() as p:
        for subfiles in progress(p.imap_unordered(functools.partial(_traverse_folder,
                                                                    session,
                                                                    output=path,
                                                                    progress=progress),
                                                  folders),
                                 desc='Traversing folders',
                                 unit='folder',
                                 total=len(folders)):
            files += subfiles

    return files


def download_main(args):
    session = args.session
    entity_id = args.entity_id
    output = args.output

    entity = core.get_entity(session, entity_id)
    if entity.type == core.FOLDER_TYPE or entity.type == core.PROJECT_TYPE:
        download_folder(session, entity, output=output)
    else:
        download_revision(session, entity_id, output=output)
