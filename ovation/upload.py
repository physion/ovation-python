import mimetypes
import os.path

import boto3
import six


def upload_revision(session, parent_file, local_path):
    """
    Upload a new `Revision` to `parent_file`. File is uploaded from `local_path` to
    the Ovation cloud, and the newly created `Revision` version is set.
    :param session: ovation.connection.Session
    :param parent_file: file entity dictionary or file ID string
    :param from_path: local path
    :return: new `Revision` entity dicitonary
    """

    if isinstance(parent_file, six.string_types):
        parent_file = session.get(session.make_type_path('file', id=parent_file))

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

    file_obj.upload_file(local_path, ExtraArgs={'ContentType': content_type,
                                                'ServerSideEncryption': 'AES256'})

    revision['attributes']['version'] = file_obj.version_id

    return session.put('/api/v1/revisions/{}'.format(revision['_id']), entity=revision)


