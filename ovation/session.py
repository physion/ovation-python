"""
Connection utilities for the Ovation Python API
"""
import collections
import os.path
import requests
import six

from six.moves.urllib_parse import urljoin

from getpass import getpass


class DataDict(dict):
    def __init__(self, *args, **kw):
        super(DataDict, self).__init__(*args, **kw)
        self.__dict__ = self


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
    session : ovation.session.Session
        A new authenticated Session

    """

    if password is None:
        pw = getpass("Ovation password: ")
    else:
        pw = password

    r = requests.post(urljoin(api, 'services/token'), json={'email': email, 'password': pw})
    if r.status_code != requests.codes.ok:
        messages = {401: "Email or password incorrect. Please check your account credentials and try again. "
                         "Please email support@ovation.io if you need assistance.",
                    500: "Unable to connect due to a server error. Our engineering team has been notified. "
                         "Please email support@ovation.io if you need assistance."}
        if r.status_code in messages.keys():
            print(messages[r.status_code])
            return
        else:
            r.raise_for_status()

    token = r.json()['token']
    return Session(token, api=api)


def simplify_response(data):
    """
    Simplifies the response from Ovation REST API for easier use in Python

    :param data: response data
    :return: Pythonified response
    """
    try:
        if len(data) == 1:
            result = list(six.itervalues(data)).pop()
        else:
            result = data


        if isinstance(result, collections.Mapping):
            return DataDict(((k,simplify_response(v)) for (k,v) in six.iteritems(result)))
        elif isinstance(result, six.string_types):
            return result
        elif isinstance(result, collections.Iterable):
            return [simplify_response(d) for d in result]
    except:
        return data


class Session(object):
    def __init__(self, token, api='https://api.ovation.io/', prefix='/api/v1'):

        self.session = requests.Session()

        self.token = token
        self.api_base = api
        self.prefix = prefix

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
        if not path.startswith(self.prefix):
            path = os.path.normpath(self.prefix + path)

        return urljoin(self.api_base, path)

    @staticmethod
    def entity_path(type, id=None):
        type = type.lower()

        if not type.endswith('s'):
            type += 's'

        path = '/' + type + '/'
        if id:
            path = path + id

        return path

    def get(self, path, **kwargs):
        r = self.session.get(self.make_url(path), **kwargs)
        r.raise_for_status()

        return simplify_response(r.json())

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

        return simplify_response(r.json())

    def post(self, path, data=None, **kwargs):
        if data is None:
            data = {}

        kwargs['json'] = data
        r = self.session.post(self.make_url(path), **kwargs)
        r.raise_for_status()

        return simplify_response(r.json())

    def delete(self, path, **kwargs):
        r = self.session.delete(self.make_url(path), **kwargs)
        r.raise_for_status()

        return r
