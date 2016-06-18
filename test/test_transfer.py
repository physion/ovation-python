from unittest.mock import Mock, sentinel, patch

from nose.tools import istest, assert_equal

import ovation.session
import ovation.transfer as transfer


@istest
def should_find_parent_path():
    assert_equal(transfer.find_parent_path('f1/f2/f3/', 'f3/'), 'f1/f2/')


@istest
@patch('ovation.upload.guess_content_type')
@patch('boto3.Session')
@patch('ovation.core.create_file')
def should_create_file(create_file, boto_session, guess_content_type):
    create_file.return_value = ovation.session.DataDict(
            {'links': ovation.session.DataDict({'self': sentinel.file_self})})

    session = Mock(spec=ovation.session.Session)
    session.post.return_value = {'entities': [{'type': 'Revision',
                                               '_id': sentinel.revision_id,
                                               'links': {'self': sentinel.revision_self},
                                               'attributes': {'name': sentinel.file_name,
                                                              'content_type': sentinel.content_type}}],
                                 'aws': [{'aws': {'key': sentinel.aws_key,
                                                  'access_key_id': sentinel.access_key_id,
                                                  'secret_access_key': sentinel.secret_access_key,
                                                  'session_token': sentinel.session_token}}]}
    session.put.return_value = sentinel.updated_revision
    session.entity_path.return_value = sentinel.put_path

    guess_content_type.return_value = sentinel.content_type

    aws_session = Mock()
    boto_session.return_value = aws_session
    s3 = Mock()
    aws_session.resource.return_value = s3
    file_obj = Mock()
    s3.Object.return_value = file_obj

    aws_response = {'VersionId': sentinel.version_id}
    file_obj.copy_from.return_value = aws_response

    assert_equal(transfer.create_file(session,
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
    session.put.assert_called_with(sentinel.revision_self,
                                   entity={'type': 'Revision',
                                           '_id': sentinel.revision_id,
                                           'links': {'self': sentinel.revision_self},
                                           'attributes': {'name': sentinel.file_name,
                                                          'version': sentinel.version_id,
                                                          'content_type': sentinel.content_type}})





@istest
@patch('boto3.Session')
def should_copy_bucket_contents(boto_session):

    session = Mock(spec=ovation.session.Session)
    project_id = 1
    aws_access_key_id = sentinel.access_key
    aws_secret_access_key = sentinel.secret_key
    source_s3_bucket = sentinel.bucket,
    destination_s3_bucket = "test2"

    aws_session = Mock()
    s3 = Mock()
    boto_session.return_value = aws_session
    aws_session.resource = Mock(return_value=s3)

    bucket = Mock()
    s3.Bucket = Mock(return_value=bucket)

    #TBD
    #Follow up wity barry regarding syntax
