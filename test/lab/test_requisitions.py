import ovation.session as session
import ovation.lab.requisitions as requisitions

from unittest.mock import sentinel, Mock, patch
from nose.tools import istest, assert_is_not_none


@istest
def should_get_all_requisitions():
    s = Mock(spec=session.Session)
    sv3 = Mock(spec=session.Session)
    s.with_prefix.return_value = sv3
    sv3.path.return_value = sentinel.requisitions_path
    sv3.get.return_value = session.simplify_response({})

    requisitions.get_requisitions(s)

    s.with_prefix.assert_called_with('/api/v3')
    sv3.path.assert_called_with('requisitions', include_org=False)
    sv3.get.assert_called_with(sentinel.requisitions_path)
