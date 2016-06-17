import copy
from unittest.mock import Mock, sentinel, patch

from nose.tools import istest, assert_equal

import ovation.session
import ovation.transfer as transfer

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
