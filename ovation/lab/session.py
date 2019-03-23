"""
Connection wrapper for Ovation Lab API
"""

from ovation.session import connect_lab, DEFAULT_LAB_HOST


def connect(email, token=None, api=DEFAULT_LAB_HOST):
    return connect_lab(email, token=token, api=DEFAULT_LAB_HOST)
