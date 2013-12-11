"""
Tools for interacting with the ovation.io API
"""
import json
import urlparse
import urllib

import requests
from requests.exceptions import ConnectionError

PROTOCOL = 'https'
HOST = 'ovation.io'
API_VERSION = 1

_codes = requests.status_codes.codes

def _api_endpoint(protocol=PROTOCOL, host=HOST, version=API_VERSION):
    '''
    Returns the API endpoint URI.
    '''
    return '{protocol}://{host}/api/v{version}'.format(protocol=protocol,
                                                       host=host,
                                                       version=version)

def _join(base, relative_url):
    return urlparse.urljoin(base, relative_url)

class WebApiException(Exception):
    def __init__(self, *args, **kwargs):
        super(WebApiException, self).__init__(*args, **kwargs)

class WebApi(object):

    def __init__(self,
                 user_email,
                 password,
                 host=HOST,
                 protocol=PROTOCOL,
                 version=API_VERSION):
        self.base_url = _api_endpoint(protocol=protocol,
                                     host=host,
                                     version=version)


        self.__email = user_email
        self.__password = password

        self._key = None


    def api_endpoint(self):
        return self.base_url



    def api_key(self):
        if self._key is None:
            auth_data = {'email' : self.__email,
                         'password' : self.__password}

            r = requests.post(_join(self.base_url, 'sessions'), data=auth_data)

            if r.status_code != _codes.ok:
                raise WebApiException("Unable to authenticate user: {0} ({1})".format(r.status_code, r.reason))

            self._key = r.json()['api_key']

        return self._key

    def jar_info(self):
        '''
        Returns download info for the Java all-in-one JAR download.exceptions

        Raises ConnectionError when offline
        '''

        api_key = self.api_key()
        r = requests.get(_join(self.base_url, 'downloads/Ovation Matlab API Core'), auth=(api_key, api_key))

        if r.status_code != _codes.ok:
            raise WebApiException("Unable to retrieve download info: {0} ({1})".format(r.status_code, r.reason))


        return r.json()
