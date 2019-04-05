"""
Connection wrapper for Ovation Lab API
"""

import ovation.session


def connect(email, token=None, api=ovation.session.DEFAULT_LAB_HOST):
    """
    Creates a new Session object with a connection to the Ovation API
    :param email: Ovation account email
    :param token: API token
    :param api: API base URL
    :return: ovation.session.Session
    """
    return ovation.session.connect(email, token=token, api=api, org=None)
