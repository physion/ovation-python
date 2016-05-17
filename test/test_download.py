from unittest.mock import sentinel, Mock

from nose.tools import istest, assert_equal

import ovation.download as download
import ovation.session as session


@istest
def should_get_download_info():
    revision = {'type': 'Revision',
                'attributes': {'url': sentinel.url}}

    s = Mock(spec=session.Session)
    s.session = Mock()
    response = Mock()
    response.json = Mock(return_value=sentinel.result)
    s.session.get = Mock(return_value=response)
    s.token = sentinel.token

    result = download.revision_download_info(s, revision)

    assert_equal(result, sentinel.result)
    s.session.get.assert_called_with(sentinel.url,
                                     headers={'accept': 'application/json'},
                                     params={'token': sentinel.token})
