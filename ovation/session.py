"""
Connection utilities for the Ovation Python API
"""
import collections
import os.path
import requests
import requests.exceptions
import six
import retrying
import json

from six.moves.urllib_parse import urljoin, urlparse
from getpass import getpass

DEFAULT_HOST = 'https://api.ovation.io'
DEFAULT_LAB_HOST = 'https://lab-services.ovation.io'
DEVELOPMENT_HOST = 'https://api-dev.ovation.io'


class DataDict(dict):
    def __init__(self, *args, **kw):
        super(DataDict, self).__init__(*args, **kw)
        self.__dict__ = self


CREDENTIALS_PATH = "~/.ovation/credentials.json"


def read_saved_token(email, url=DEFAULT_HOST, credentials_path=CREDENTIALS_PATH):
    path = os.path.expanduser(credentials_path)
    o = urlparse(url)
    host = o.netloc
    if os.path.exists(path):
        with open(path, 'r') as f:
            creds = json.load(f)
            if host in creds:
                if email in creds[host]:
                    return creds[host][email]

    return None


def connect_lab(email, token=None, api=DEFAULT_LAB_HOST):
    return connect(email, token=token, api=api, org=None)

def connect(email, token=None, api=DEFAULT_HOST, org=0):
    """Creates a new Session.
    
    Arguments
    ---------
    email : string
        Ovation.io account email. Required for selection of saved token.

    token : string, optional
        Ovation.io API token.

    org : integer, optional
        Organization Id. Default 0 indicates Personal Projects.
    
    Returns
    -------
    session : ovation.session.Session
        A new authenticated Session

    """

    saved_token = read_saved_token(email, url=api)
    if saved_token:
        return Session(saved_token, api=api, org=org)

    if token is None:
        token = getpass("Ovation API token: ")

    return Session(token, api=api, org=org)


def simplify_response(data, hoist_singleton=True):
    """
    Simplifies the response from Ovation REST API for easier use in Python

    :param data: response data
    :return: Pythonified response
    """
    try:
        if len(data) == 1 and hoist_singleton:
            result = list(six.itervalues(data)).pop()
        else:
            result = data

        if isinstance(result, collections.Mapping):
            if 'type' in result and result['type'] == 'Annotation':
                return DataDict(result)

            return DataDict(((k, simplify_response(v, hoist_singleton=False)) for (k, v) in six.iteritems(result)))
        elif isinstance(result, six.string_types):
            return result
        elif isinstance(result, collections.Iterable):
            return [simplify_response(d) for d in result]
    except:
        return data


MAX_RETRY_DELAY_MS = 2000
MIN_RETRY_DELAY_MS = 250


def _retry_if_http_error(exception):
    """Return True if we should retry (in this case when it's an RequestException), False otherwise"""
    return isinstance(exception, requests.exceptions.RequestException)


class Session(object):
    """
    Represents an authenticated session.

    `Session` wraps a `requests.Session` and provides methods for convenient creation of Ovation API paths and URLs.
    All responses are transformed via `simplify_response` to make interactive use more convenient.
    """

    def __init__(self, token, api=DEFAULT_HOST, prefix='/api/v1', retry=3, org=0):
        """
        Creates a new Session
        :param token: Ovation API token
        :param api: API endpoint URL (default https://api.ovation.io)
        :param prefix: API namespace prefix (default '/api/v1')
        :param retry: number of retries API calls will retry on failure. If 0, no retry.
        :param org: Organization Id. Default (0) indicates personal projects.
        :return: Session object
        """
        self.session = requests.Session()

        self.token = token
        self.api_base = api
        self.prefix = prefix
        self.retry = retry if retry is not None else 0
        self.org = org

        class BearerAuth(object):
            def __init__(self, token):
                self.token = token

            def __call__(self, r):
                # modify and return the request
                r.headers['Authorization'] = 'Bearer {}'.format(self.token)
                return r

        self.session.auth = BearerAuth(token)
        self.session.headers = {'content-type': 'application/json',
                                'accept': 'application/json'}

    def json(self):
        return json.dumps({'token': self.token,
                           'api_base': self.api_base,
                           'prefix': self.prefix,
                           'retry': self.retry})

    @staticmethod
    def from_json(json_string):
        d = json.loads(json_string)
        return Session(d['token'],
                       api=d['api_base'],
                       prefix=d['prefix'],
                       retry=d['retry'])

    def refresh(self):
        pass

    def make_url(self, path):
        """
        Creates a full URL by combining the API host, prefix and the provided path
        :param path: path, e.g. /projects/1
        :return: full URL, e.g. https://api.ovation.io/api/v1/projects/1
        """
        if not path.startswith(self.prefix):
            path = (self.prefix + path).replace('//', '/')

        return urljoin(self.api_base, path)

    def path(self, resource='entities', entity_id=None, org=None, include_org=True):
        """Makes a resource path
        
            >>> Session.path('projects')
            /api/v1/projects
        
        :param resource: Entity name (e.g. "project" or "projects"). Pluralization will be added if needed
        :param entity_id: Optional single entity ID
        :return: complete resource path
        """

        organization_id = org if org is not None else self.org

        resource = resource.lower()

        if not resource.endswith('s'):
            resource += 's'

        if include_org and (organization_id is not None):
            path = '/o/{org}/{resource}/'.format(org=organization_id, resource=resource)
        else:
            path = '/{resource}/'.format(org=organization_id, resource=resource)

        if entity_id:
            path = path + str(entity_id)

        return path

    def retry_call(self, m, *args, **kwargs):
        return retrying.Retrying(stop_max_attempt_number=self.retry + 1,
                                 wait_exponential_multiplier=MIN_RETRY_DELAY_MS,  # MS
                                 wait_exponential_max=MAX_RETRY_DELAY_MS,
                                 wait_jitter_max=MIN_RETRY_DELAY_MS,
                                 retry_on_exception=_retry_if_http_error).call(m, *args, **kwargs)

    def get(self, path, **kwargs):
        r = self.retry_call(self._get, path, **kwargs)

        return simplify_response(r.json())

    def _get(self, path, **kwargs):
        r = self.session.get(self.make_url(path), **kwargs)
        r.raise_for_status()
        return r

    def put(self, path, entity=None, data=None, **kwargs):
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

            if 'entities' in path:
                data = {"entity": entity}
            else:
                data = {entity['type'].lower(): entity}
        else:
            if data is None:
                data = {}

        kwargs['json'] = data
        r = self.retry_call(self._put, path, **kwargs)

        return simplify_response(r.json())

    def _put(self, path, **kwargs):
        r = self.session.put(self.make_url(path), **kwargs)
        r.raise_for_status()
        return r

    def post(self, path, data=None, **kwargs):
        if data is None:
            data = {}

        kwargs['json'] = data
        r = self.retry_call(self._post, path, **kwargs)

        return simplify_response(r.json())

    def _post(self, path, **kwargs):
        r = self.session.post(self.make_url(path), **kwargs)
        r.raise_for_status()
        return r

    def delete(self, path, **kwargs):
        return self.retry_call(self._delete, path, **kwargs)

    def _delete(self, path, **kwargs):
        r = self.session.delete(self.make_url(path), **kwargs)
        r.raise_for_status()
        return r
