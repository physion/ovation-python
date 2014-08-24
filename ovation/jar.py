"""
Tools for updating the Ovation API Jar
"""
import json

import platform
import os
import logging
import sys
import progressbar

import six.moves.urllib as urllib

from ovation.web import WebApi


def jar_directory(system=platform.system()):
    return _default_jar_directory(system)

def _default_jar_directory(system=platform.system()):
    _default = {
        'Windows': os.path.join('~', 'AppData', 'Local', 'ovation', 'python'),
        'Darwin': os.path.join('~', 'Library', 'Application Support', 'us.physion.ovation', 'python'),
        'Linux': os.path.join('~', '.ovation', 'python')
    }

    return _default[system]

def _download(url, file_name):
    u = urllib.urlopen(url)
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])

    with open(file_name, 'wb') as f:
        file_size_dl = 0
        block_sz = 8192
        bar = progressbar.ProgressBar(maxval=100,
                                        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            progress = file_size_dl * 100. / file_size
            bar.update(int(progress))
        bar.finish()


class JarUpdater(object):
    def __init__(self, user_email, password, jar_directory=None, web=None, downloader=_download):
        if jar_directory is None:
            jar_directory = _default_jar_directory()

        if web is None:
            web = WebApi(user_email, password)

        self.jar_directory = os.path.expanduser(jar_directory)
        self.web_api = web
        self.downloader = downloader


    def _etag_file(self):
        return os.path.join(self.jar_directory, 'ovation.jar.etag')

    def _read_etag(self):
        if os.path.exists(self._etag_file()):
            with open(self._etag_file()) as f:
                info = json.load(f)
                return info['etag']

        return None

    def _write_etag(self, info):
        with open(self._etag_file(), 'w') as f:
            json.dump(info, f)

    def update_jar(self):
        info = self.web_api.jar_info()

        if not self._read_etag() == info['etag']:
            if not os.path.exists(self.jar_directory):
                os.makedirs(self.jar_directory)

            logging.info("Updating Ovation API")
            print("Updating Ovation API...")
            self.downloader(info['url'], os.path.join(self.jar_directory, 'ovation.jar'))
            self._write_etag(info)

            return True

        return False



