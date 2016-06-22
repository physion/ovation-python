import copy
from unittest.mock import Mock, sentinel, patch

from nose.tools import istest, assert_equal

import ovation.session
import ovation.upload as revisions

@istest
@patch('boto3.Session')
def should_create_revision(boto_session):
    file = {'type': 'File',
            'links': {'self': sentinel.self}}
    path = '/local/path/file.txt'
    rev = {'_id': 1,
           'type': 'Revision',
           'attributes': {'url': sentinel.url},
           'links': {'upload-complete': sentinel.upload_complete}}

    s = Mock(spec=ovation.session.Session)

    def entity_path(type='', id=''):
        return "/api/v1/{}/{}".format(type, id)

    s.entity_path.side_effect = entity_path
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
    result = revisions.upload_revision(s, file, path)

    # Assert
    boto_session.assert_called_with(aws_access_key_id=sentinel.access_key,
                                    aws_secret_access_key=sentinel.secret_key,
                                    aws_session_token=sentinel.session_token)
    s3.Object.assert_called_with(sentinel.bucket, sentinel.key)
    file_obj.upload_file.assert_called_with(path, ExtraArgs={'ContentType': 'text/plain',
                                                             'ServerSideEncryption': 'AES256'})

    s.put.assert_called_with(sentinel.upload_complete, entity=None)

    assert_equal(result, sentinel.result)




