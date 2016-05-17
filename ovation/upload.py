import mimetypes
import os.path
import threading

import boto3
import six

import ovation.core as core

from tqdm import tqdm


class ProgressPercentage(object):
    def __init__(self, filename, progress=tqdm):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._size = float(os.path.getsize(filename))
        self._progress = progress(unit='B',
                                  unit_scale=True,
                                  total=self._size,
                                  desc=os.path.basename(filename))

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            self._progress.update(self._seen_so_far)
            if self._seen_so_far >= self._size:
                self._progress.close()


def upload_folder(session, parent, directory_path, progress=tqdm):
    """
    Recursively uploads a folder to Ovation

    :param session: Session
    :param parent: Project or Folder root
    :param directory_path: local path to directory
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    """

    root_folder = parent
    for root, dirs, files in os.walk(directory_path):
        root_folder = core.create_folder(session, root_folder, os.path.basename(root))

        for f in files:
            path = os.path.join(root, f)
            file = core.create_file(session, root_folder, f)

            upload_revision(session, file, path, progress=progress)

def upload_file(session, parent, file_path, progress=tqdm):
    """
    Upload a file to Ovation

    :param session: Session
    :param parent: Project or Folder root
    :param file_path: local path to file
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    :return: created File entity dictionary
    """
    name = os.path.basename(file_path)
    file = core.create_file(session, parent, name)
    return upload_revision(session, file, file_path, progress=progress)


def upload_revision(session, parent_file, local_path, progress=tqdm):
    """
    Upload a new `Revision` to `parent_file`. File is uploaded from `local_path` to
    the Ovation cloud, and the newly created `Revision` version is set.
    :param session: ovation.connection.Session
    :param parent_file: file entity dictionary or file ID string
    :param local_path: local path
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    :return: new `Revision` entity dicitonary
    """

    if isinstance(parent_file, six.string_types):
        parent_file = session.get(session.entity_path('file', id=parent_file))

    file_name = os.path.basename(local_path)
    content_type = mimetypes.guess_type(file_name)[0]
    if content_type is None:
        content_type = 'application/octet-stream'

    r = session.post(parent_file['links']['self'],
                     data={'entities': [{'type': 'Revision',
                                         'attributes': {'name': file_name,
                                                        'content_type': content_type}}]})
    revision = r['entities'][0]
    aws = r['aws'][0]['aws']

    aws_session = boto3.Session(aws_access_key_id=aws['access_key_id'],
                                aws_secret_access_key=aws['secret_access_key'],
                                aws_session_token=aws['session_token'])
    s3 = aws_session.resource('s3')

    file_obj = s3.Object(aws['bucket'], aws['key'])

    args = {'ContentType': content_type,
            'ServerSideEncryption': 'AES256'}
    if progress and os.path.exists(local_path):
        file_obj.upload_file(local_path, ExtraArgs=args,
                             Callback=ProgressPercentage(local_path, progress=progress))
    else:
        file_obj.upload_file(local_path, ExtraArgs=args)

    revision['attributes']['version'] = file_obj.version_id

    return session.put('/api/v1/revisions/{}'.format(revision['_id']), entity=revision)
