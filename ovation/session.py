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


def connect(email, password=None, api=DEFAULT_HOST, token='services/token'):
    """Creates a new Session.
    
    Arguments
    ---------
    email : string
        Ovation.io account email
    
    password : string, optional
        Ovation.io account password. If omitted, the password will be prompted.
    
    Returns
    -------
    session : ovation.session.Session
        A new authenticated Session

    """

    saved_token = read_saved_token(email, url=api)
    if saved_token:
        return Session(saved_token, api=api)

    if password is None:
        pw = getpass("Ovation password: ")
    else:
        pw = password

    r = requests.post(urljoin(api, token), json={'email': email, 'password': pw})
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

    def __init__(self, token, api='https://api.ovation.io', prefix='/api/v1', retry=3):
        """
        Creates a new Session
        :param token: Ovation API token
        :param api: API endpoint URL (default https://api.ovation.io)
        :param prefix: API namespace prefix (default '/api/v1')
        :param retry: number of retries API calls will retry on failure. If 0, no retry.
        :return: Session object
        """
        self.session = requests.Session()

        self.token = token
        self.api_base = api
        self.prefix = prefix
        self.retry = retry if retry is not None else 0

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
        """
        Creates a full URL by combining the API host, prefix and the provided path
        :param path: path, e.g. /projects/1
        :return: full URL, e.g. https://api.ovation.io/api/v1/projects/1
        """
        if not path.startswith(self.prefix):
            path = os.path.normpath(self.prefix + path)

        return urljoin(self.api_base, path)

    @staticmethod
    def entity_path(resource='entities', entity_id=None):
        resource = resource.lower()

        if not resource.endswith('s'):
            resource += 's'

        path = '/' + resource + '/'
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
