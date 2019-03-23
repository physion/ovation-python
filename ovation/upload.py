import logging
import mimetypes
import threading
import boto3
import six
import os
import math

import ovation.core as core

from boto3.s3.transfer import TransferConfig
from tqdm import tqdm


class ProgressCallback(object):
    def __init__(self, filename, progress=tqdm):
        self._filename = filename
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
            self._progress.update(bytes_amount)
            if bytes_amount >= self._size:
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
        root_name = os.path.basename(root)
        if len(root_name) == 0:
            root_name = os.path.basename(os.path.dirname(root))

        root_folder = core.create_folder(session, root_folder, root_name)

        for f in files:
            path = os.path.join(root, f)
            file = core.create_file(session, root_folder, f)

            upload_revision(session, file, path, progress=progress)


def upload_file(session,
                parent,
                local_path_or_file_obj,
                name=None,
                content_type=None,
                progress=tqdm):
    """
    Upload a file to Ovation

    :param session: Session
    :param parent: Project or Folder root
    :param local_path_or_file_obj: local path to file
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    :param content_type: revision content type (default: infer from file name)
    :param name: file name (default: local path basename)
    :return: created File entity dictionary
    """

    if name is None:
        name = os.path.basename(local_path_or_file_obj)

    file = core.create_file(session, parent, name)
    return upload_revision(session,
                           file,
                           local_path_or_file_obj,
                           content_type=content_type,
                           file_name=name,
                           progress=progress)


def guess_content_type(file_name):
    content_type = mimetypes.guess_type(file_name)[0]
    if content_type is None:
        content_type = 'application/octet-stream'

    return content_type


MAX_PARTS = 10000
MB = boto3.s3.transfer.MB
GB = MB * 1024


def multipart_chunksize(n_bytes):
    """
    Calculates the correct chunk size for a file of n_bytes
    :param n_bytes: file size (bytes)
    :return: multipart chunk size (bytes)
    """

    chunk_size = math.ceil(n_bytes / MAX_PARTS)

    return max(chunk_size, 8 * MB)


def upload_revision(session,
                    parent_file,
                    local_path,
                    progress=tqdm,
                    chunk_size=multipart_chunksize,
                    content_type=None,
                    file_name=None):
    """
    Upload a new `Revision` to `parent_file`. File is uploaded from `local_path` to
    the Ovation cloud, and the newly created `Revision` version is set.
    :param chunk_size: function that returns desired multi-part upload chunk size given file path
    :param session: ovation.connection.Session
    :param parent_file: file entity dictionary or file ID string
    :param local_path: local path
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    :param content_type: revision content type (default: infer from file name)
    :param file_name: revision file name (default: infer from local path)
    :return: new `Revision` entity dicitonary
    """

    if isinstance(parent_file, six.string_types):
        parent_file = session.get(session.path('file', entity_id=parent_file))

    if file_name is None:
        file_name = os.path.basename(local_path)

    if content_type is None:
        content_type = guess_content_type(file_name)

    r = session.post(parent_file['links']['self'],
                     data={'entities': [{'type': 'Revision',
                                         'attributes': {'name': file_name,
                                                        'content_type': content_type}}]})
    revision = r['entities'][0]
    aws = r['aws'][0]['aws']  # Returns an :aws for each created Revision

    try:
        upload_to_aws(aws, content_type, local_path, progress, chunk_size=chunk_size)
        return session.put(revision['links']['upload-complete'], entity=None)
    except Exception as err:
        logging.error("Error during upload: {}".format(err))
        return session.put(revision['links']['upload-failed'], entity=None)


def upload_to_aws(aws,
                  content_type,
                  local_path_or_fileobj,
                  progress,
                  chunk_size=multipart_chunksize):
    aws_session = boto3.Session(aws_access_key_id=aws['access_key_id'],
                                aws_secret_access_key=aws['secret_access_key'],
                                aws_session_token=aws['session_token'])
    s3 = aws_session.resource('s3')
    file_obj = s3.Object(aws['bucket'], aws['key'])
    args = {'ContentType': content_type,
            'ServerSideEncryption': 'AES256'}

    if isinstance(local_path_or_fileobj, six.string_types):
        transfer_config = TransferConfig(multipart_chunksize=chunk_size(os.path.getsize(local_path_or_fileobj)))

        if progress:
            file_obj.upload_file(local_path_or_fileobj,
                                 ExtraArgs=args,
                                 Callback=ProgressCallback(local_path_or_fileobj, progress=progress),
                                 Config=transfer_config)
        else:
            file_obj.upload_file(local_path_or_fileobj,
                                 ExtraArgs=args,
                                 Config=transfer_config)
    else:
        if progress:
            file_obj.upload_fileobj(local_path_or_fileobj,
                                    ExtraArgs=args,
                                    Callback=ProgressCallback(local_path_or_fileobj, progress=progress))
        else:
            file_obj.upload_fileobj(local_path_or_fileobj,
                                    ExtraArgs=args)


def upload_paths(args):
    session = args.session
    parent_id = args.parent_id
    paths = args.paths
    if paths is None:
        return

    for p in paths:
        print('Uploading {}'.format(p))
        if os.path.isdir(p):
            upload_folder(session, parent_id, p)
        else:
            upload_file(session, parent_id, p)
