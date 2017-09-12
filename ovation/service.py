"""
For Python services with an API service token
"""
import json
import requests
import time

from six.moves import urllib

import ovation.session as session

DEFAULT_AUTH_DOMAIN = 'https://ovation.auth0.com/'


def get_service_token(client_id, client_secret,
                      audience='https://api.ovation.io/',
                      auth=DEFAULT_AUTH_DOMAIN):
    """Creates a new session for a service account.

    Arguments
    ---------
    client_id : string
        Service account Client ID

    client_secret : string
        Service account Client Secret

    audience : string, optional
        API audience. Default: https://api.ovation.io/

    auth : string, optional
        Authorization domain. Default: https://ovation.auth0.com

    Returns
    -------
    token_info : Dict
        Session token info. Pass this to make_session.
    """

    token_url = urllib.parse.urljoin(auth, '/oauth/token')
    body = {'client_id': client_id,
            'client_secret': client_secret,
            'audience': audience,
            'grant_type': 'client_credentials'}

    response = requests.post(token_url,
                             json=body)

    response.raise_for_status()

    token = response.json()

    expires_at = token['expires_in'] + time.time()

    token['expires_at'] = expires_at

    return token


def make_session(token_info,
                 organization=0,
                 client_id=None,
                 client_secret=None,
                 auth=DEFAULT_AUTH_DOMAIN,
                 audience='https://api.ovation.io/',
                 api=session.DEFAULT_HOST):
    """

    :param token_info:
    :param organization:
    :param client_id:
    :param client_secret:
    :param auth:
    :param audience:
    :param api:
    :return: tuple((updated) token info, session)
    """
    if (token_info is None) or (time.time() > token_info['expires_at'] and
                                        (client_id is not None) and
                                        (client_secret is not None)):
        token_info = get_service_token(client_id=client_id,
                                       client_secret=client_secret,
                                       auth=auth,
                                       audience=audience)

    s = session.Session(token_info['access_token'],
                        org=organization,
                        api=api)

    return (token_info, s)
