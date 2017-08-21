import os.path
import ovation.session
import ovation.transfer as transfer
from ovation.session import DataDict

from unittest.mock import Mock, sentinel, patch, call
from nose.tools import istest, assert_equal, with_setup


def setup():
    pass


def teardown():
    if os.path.isfile('.checkpoint.csv'):
        os.remove('.checkpoint.csv')


@istest
@patch('ovation.upload.guess_content_type')
@patch('boto3.Session')
@patch('ovation.core.create_file')
@with_setup(setup, teardown)
def should_create_file(create_file, boto_session, guess_content_type):
    create_file.return_value = ovation.session.DataDict(
            {'links': ovation.session.DataDict({'self': sentinel.file_self})})

    session = Mock(spec=ovation.session.Session)
    session.post.return_value = {'entities': [{'type': 'Revision',
                                               '_id': sentinel.revision_id,
                                               'links': {'self': sentinel.revision_self,
                                                         'upload-complete': sentinel.update_complete},
                                               'attributes': {'name': sentinel.file_name,
                                                              'content_type': sentinel.content_type}}],
                                 'aws': [{'aws': {'key': sentinel.aws_key,
                                                  'access_key_id': sentinel.access_key_id,
                                                  'secret_access_key': sentinel.secret_access_key,
                                                  'session_token': sentinel.session_token}}]}
    session.put.return_value = sentinel.updated_revision
    session.path.return_value = sentinel.put_path

    guess_content_type.return_value = sentinel.content_type

    aws_session = Mock()
    boto_session.return_value = aws_session
    s3 = Mock()
    aws_session.resource.return_value = s3
    file_obj = Mock()
    s3.Object.return_value = file_obj

    aws_response = {'VersionId': sentinel.version_id}
    file_obj.copy_from.return_value = aws_response

    assert_equal(transfer.copy_file(session,
                                    sentinel.parent_folder_id,
                                    sentinel.file_key,
                                    sentinel.file_name,
                                    sentinel.source_bucket,
                                    sentinel.dest_bucket,
                                    sentinel.global_access_key_id,
                                    sentinel.gobal_secret_access_key),
                 sentinel.updated_revision)

    session.post.assert_called_with(sentinel.file_self,
                                    data={'entities': [{'type': 'Revision',
                                                        'attributes': {'name': sentinel.file_name,
                                                                       'content_type': sentinel.content_type}}]})
    file_obj.copy_from.assert_called_with(CopySource='{}/{}'.format(sentinel.source_bucket, sentinel.file_key))
    session.put.assert_called_with(sentinel.update_complete,
                                   entity=None)


def mock_copy_file(session, parent=None, file_key=None, file_name=None, source_bucket=None,
                   destination_bucket=None, aws_access_key_id=None, aws_secret_access_key=None):
    return {'_id': sentinel.revision1}


@istest
@patch('ovation.transfer._make_session')
@patch('ovation.core.create_folder')
@patch('boto3.Session')
@with_setup(setup, teardown)
def should_copy_bucket_contents(boto_session, create_folder, make_session):
    aws_session = Mock()
    s3 = Mock()
    bucket = Mock()

    boto_session.return_value = aws_session
    aws_session.resource.return_value = s3
    s3.Bucket.return_value = bucket

    keys = [DataDict({'key': 'f1/'}),
            DataDict({'key': 'f1/f2/'}),
            DataDict({'key': 'f1/f2/f3/'}),
            DataDict({'key': 'f1/file1.txt'})]

    bucket.objects.all.return_value = keys

    create_folder.side_effect = [{'_id': sentinel.f1}, {'_id': sentinel.f2}, {'_id': sentinel.f3}]

    make_session.return_value = sentinel.ov_session

    session = DataDict({'token': sentinel.ov_session_token})

    r = transfer.copy_bucket_contents(session,
                                      project=sentinel.project,
                                      aws_access_key_id=sentinel.access_key_id,
                                      aws_secret_access_key=sentinel.secret_access_key,
                                      source_s3_bucket=sentinel.src_bucket,
                                      destination_s3_bucket=sentinel.dest_bucket,
                                      copy_file_fn=mock_copy_file)

    assert_equal(set(map(str, r.values())), set(map(str, {sentinel.revision1, sentinel.f1, sentinel.f2, sentinel.f3})))
