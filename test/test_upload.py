import copy
import math
import boto3
from unittest.mock import Mock, sentinel, patch, ANY

from nose.tools import istest, assert_equal

import ovation.session
import ovation.upload as upload

from boto3.s3.transfer import TransferConfig

@istest
@patch('os.path.getsize')
@patch('boto3.Session')
def should_create_revision(boto_session, getsize):
    file = {'type': 'File',
            'links': {'self': sentinel.self}}
    path = '/local/path/file.txt'
    rev = {'_id': 1,
           'type': 'Revision',
           'attributes': {'url': sentinel.url},
           'links': {'upload-complete': sentinel.upload_complete}}

    getsize.return_value = 100

    s = Mock(spec=ovation.session.Session)

    def entity_path(type='', id=''):
        return "/api/v1/{}/{}".format(type, id)

    s.path.side_effect = entity_path
    aws_session = Mock()
    s3 = Mock()
    boto_session.return_value = aws_session
    aws_session.resource = Mock(return_value=s3)

    file_obj = Mock()
    s3.Object = Mock(return_value=file_obj)
    file_obj.upload_file = Mock()
    file_obj.version_id = sentinel.version

    s.post = Mock(return_value={'entities': [rev],
                                'aws': [{'aws': dict(access_key_id=sentinel.access_key,
                                                     secret_access_key=sentinel.secret_key,
                                                     session_token=sentinel.session_token,
                                                     bucket=sentinel.bucket,
                                                     key=sentinel.key)}]})

    s.put = Mock(return_value=sentinel.result)

    # Act
    result = upload.upload_revision(s, file, path, progress=None)

    # Assert
    boto_session.assert_called_with(aws_access_key_id=sentinel.access_key,
                                    aws_secret_access_key=sentinel.secret_key,
                                    aws_session_token=sentinel.session_token)
    s3.Object.assert_called_with(sentinel.bucket, sentinel.key)
    file_obj.upload_file.assert_called_with(path,
                                            ExtraArgs={'ContentType': 'text/plain',
                                                       'ServerSideEncryption': 'AES256'},
                                            Config=ANY)

    s.put.assert_called_with(sentinel.upload_complete, entity=None)

    assert_equal(result, sentinel.result)


@istest
@patch('os.path.getsize')
@patch('boto3.Session')
def should_create_revision_from_file_obj(boto_session, getsize):
    file = {'type': 'File',
            'links': {'self': sentinel.self}}
    open_file_obj = sentinel.file_obj
    rev = {'_id': 1,
           'type': 'Revision',
           'attributes': {'url': sentinel.url},
           'links': {'upload-complete': sentinel.upload_complete}}

    getsize.return_value = 100

    s = Mock(spec=ovation.session.Session)

    def entity_path(type='', id=''):
        return "/api/v1/{}/{}".format(type, id)

    s.path.side_effect = entity_path
    aws_session = Mock()
    s3 = Mock()
    boto_session.return_value = aws_session
    aws_session.resource = Mock(return_value=s3)

    file_obj = Mock()
    s3.Object = Mock(return_value=file_obj)
    file_obj.upload_file = Mock()
    file_obj.version_id = sentinel.version

    s.post = Mock(return_value={'entities': [rev],
                                'aws': [{'aws': dict(access_key_id=sentinel.access_key,
                                                     secret_access_key=sentinel.secret_key,
                                                     session_token=sentinel.session_token,
                                                     bucket=sentinel.bucket,
                                                     key=sentinel.key)}]})

    s.put = Mock(return_value=sentinel.result)

    # Act
    result = upload.upload_revision(s,
                                    file,
                                    open_file_obj,
                                    content_type='text/plain',
                                    file_name='my-file',
                                    progress=None)

    # Assert
    boto_session.assert_called_with(aws_access_key_id=sentinel.access_key,
                                    aws_secret_access_key=sentinel.secret_key,
                                    aws_session_token=sentinel.session_token)
    s3.Object.assert_called_with(sentinel.bucket, sentinel.key)
    file_obj.upload_fileobj.assert_called_with(open_file_obj,
                                               ExtraArgs={'ContentType': 'text/plain',
                                                          'ServerSideEncryption': 'AES256'})

    s.put.assert_called_with(sentinel.upload_complete, entity=None)

    assert_equal(result, sentinel.result)

@istest
@patch('os.path.getsize')
@patch('boto3.Session')
def should_set_multipart_chunk_size(boto_session, getsize):
    file = {'type': 'File',
            'links': {'self': sentinel.self}}
    path = '/local/path/file.txt'
    rev = {'_id': 1,
           'type': 'Revision',
           'attributes': {'url': sentinel.url},
           'links': {'upload-complete': sentinel.upload_complete,
                     'upload-failed': sentinel.upload_failed}}

    getsize.return_value = sentinel.file_size

    s = Mock(spec=ovation.session.Session)

    def entity_path(type='', id=''):
        return "/api/v1/{}/{}".format(type, id)

    s.path.side_effect = entity_path
    aws_session = Mock()
    s3 = Mock()
    boto_session.return_value = aws_session
    aws_session.resource = Mock(return_value=s3)

    file_obj = Mock()
    s3.Object = Mock(return_value=file_obj)
    file_obj.upload_file = Mock()
    file_obj.version_id = sentinel.version

    CHUNK_SIZE=100000
    _chunk_size = Mock(return_value=CHUNK_SIZE)

    s.post = Mock(return_value={'entities': [rev],
                                'aws': [{'aws': dict(access_key_id=sentinel.access_key,
                                                     secret_access_key=sentinel.secret_key,
                                                     session_token=sentinel.session_token,
                                                     bucket=sentinel.bucket,
                                                     key=sentinel.key)}]})

    s.put = Mock(return_value=sentinel.result)

    # Act
    upload.upload_revision(s, file, path, chunk_size=_chunk_size, progress=None)

    # Assert
    call = file_obj.upload_file.call_args_list[0]
    assert_equal(call[1]['Config'].multipart_chunksize, CHUNK_SIZE)


@istest
def calculates_chunk_size_for_large_file():
    nbytes = 180 * upload.GB
    cs = upload.multipart_chunksize(nbytes)
    assert_equal(cs, math.ceil(nbytes/upload.MAX_PARTS))

@istest
def calculates_chunk_size_for_small_file():
    nbytes = 1000
    cs = upload.multipart_chunksize(nbytes)

    assert_equal(cs, 8 * upload.MB)

@istest
def MB_is_mega():
    assert_equal(upload.MB, boto3.s3.transfer.MB)

