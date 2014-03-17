import json
import os
import tempfile
import mock
import nose
from nose.tools import istest, assert_equals, assert_is_not_none, assert_false
from ovation.jar import _default_jar_directory, JarUpdater


@istest
def should_have_osx_jar_directory():
    expected = os.path.join('~', 'Library', 'Application Support', 'us.physion.ovation', 'python')

    assert_equals(expected, _default_jar_directory('Darwin'))

@istest
def should_have_windows_jar_directory():
    expected = os.path.join('~', 'AppData', 'Local', 'ovation', 'python')

    assert_equals(expected, _default_jar_directory('Windows'))

@istest
def should_have_linux_jar_directory():
    expected = os.path.join('~', '.ovation', 'python')

    assert_equals(expected, _default_jar_directory('Linux'))


@istest
def should_have_jar_directory():
    updater = JarUpdater("", "")
    assert_is_not_none(updater.jar_directory)


@istest
def should_have_web_api():
    updater = JarUpdater("foo", "foo")
    assert_is_not_none(updater.web_api)



@istest
def should_get_jar_info():
    web = mock.Mock()
    info_response = {
        u'etag': u'should_get_jar_info',
        u'url': u'https://ovation-download/ovation-with-dependencies-2.1.11.jar'
    }
    web.jar_info.return_value = info_response

    updater = JarUpdater("email", "password",
                         web=web,
                         downloader=mock.Mock(),
                         jar_directory=tempfile.gettempdir())

    updater.update_jar()

    web.jar_info.assert_called_with()

def teardown():
    etag_path = os.path.join(tempfile.gettempdir(), 'ovation.jar.etag')
    if os.path.exists(etag_path):
        os.remove(etag_path)

@istest
def should_download_jar():
    web = mock.Mock()
    info_response = {
        u'etag': u'should_download_jar',
        u'url': u'https://ovation-download/ovation-with-dependencies-2.1.11.jar'
    }
    web.jar_info.return_value = info_response

    dl = mock.Mock()

    updater = JarUpdater("email", "password",
                         web=web,
                         downloader=dl,
                         jar_directory=tempfile.gettempdir())

    updater.update_jar()

    dl.assert_called_with(info_response['url'], os.path.join(updater.jar_directory, 'ovation.jar'))


@istest
def should_not_download_current_jar():
    web = mock.Mock()
    info_response = {
        u'etag': u'should_not_download_current_jar',
        u'url': u'https://ovation-download/ovation-with-dependencies-2.1.11.jar'
    }
    web.jar_info.return_value = info_response

    # write the etag
    jar_dir = tempfile.gettempdir()
    with open(os.path.join(jar_dir, 'ovation.jar.etag'), 'w') as f:
        json.dump(info_response, f)

    dl = mock.NonCallableMock()

    updater = JarUpdater("email", "password",
                         web=web,
                         downloader=dl,
                         jar_directory=jar_dir)

    updater.update_jar()

