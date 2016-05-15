"""
Connection utilities for the Ovation Python API
"""

import requests
import six

if six.PY2:
    from urlparse import urljoin
elif six.PY3:
    from urllib.parse import urljoin

from getpass import getpass


def connect(email, password=None, api='https://api.ovation.io'):
    """Creates a new Session.
    
    Arguments
    ---------
    email : string
        Ovation.io account email
    
    password : string, optional
        Ovation.io account passowrd. If ommited, the password will be prompted at the command prompt
    
    Returns
    -------
    session : ovation.connection.Session
        A new authenticated Session

    """

    if password is None:
        pw = getpass("Ovation password: ")
    else:
        pw = password

    r = requests.post(urljoin(api, 'services/token'), json={'email': email, 'password': pw})
    r.raise_for_status()

    token = r.json()['token']
    return Session(token, api=api)


class Session(object):
    def __init__(self, token, api='https://api.ovation.io'):

        self.session = requests.Session()

        self.token = token
        self.api_base = api

        class BearerAuth(object):
            def __init__(self, token):
                self.token = token

            def __call__(self, r):
                # modify and return the request
                r.headers['Authorization'] = 'Bearer {}'.format(self.token)
                return r

        self.session.auth = BearerAuth(token)
        self.session.headers = {'content-type': 'application/json'}

    def refresh(self):
        pass

    def make_url(self, path):
        return urljoin(self.api_base, path)

    def get(self, path, **kwargs):
        r = self.session.get(self.make_url(path), **kwargs)
        r.raise_for_status()

        return r.json()

    def put(self, path, entity=None, **kwargs):
        """

        :param path: entity path
        :param entity: entity dictionary
        :param kwargs: additional args for requests.Session.put
        :return:
        """

        if entity is not None:
            if 'links' in entity:
                del entity['links']
            if 'relationships' in entity:
                del entity['relationships']
            if 'owner' in entity:
                del entity['owner']

            data = {entity['type'].lower(): entity}
        else:
            data = {}

        kwargs['json'] = data
        r = self.session.put(self.make_url(path), **kwargs)
        r.raise_for_status()

        return r.json()

    def post(self, path, data=None, **kwargs):
        if data is None:
            data = {}

        kwargs['json'] = data
        r = self.session.post(self.make_url(path), **kwargs)
        r.raise_for_status()

        return r.json()

    def delete(self, path, **kwargs):
        r = self.session.delete(self.make_url(path), **kwargs)
        r.raise_for_status()

        return r
