"""Testing utilities for code that runs against an Ovation database"""
from unittest import TestCase

import uuid
from contextlib import contextmanager

from ovation.api import OvationApiModule
from ovation.test.util import TestUtils



def __make_local_stack():
    """Builds a local database stack"""

    testUtils = TestUtils()
    userId = uuid.uuid4()
    userIdentity = unicode(str(userId) + "@email.com")
    userPassword = u"password"

    databaseName = userIdentity.replace("@", "-").replace(".", "-")

    localStack = testUtils.makeLocalStack(OvationApiModule(),
                                          databaseName,
                                          userIdentity,
                                          userPassword)

    return (localStack, userIdentity, userPassword)


def make_local_stack():
    stack, userIdentity, userPassword = __make_local_stack()
    dsc = stack.getAuthenticatedDataStoreCoordinator()

    return (stack, dsc)


@contextmanager
def local_stack():
    """Context manager wrapping a local database stack. This stack uses a local, transient cloud storage endpoint and
    a local CouchDB database in place of a normal ovation.io account database.
    
    This manager yields an authenticated DataStoreCoordinator for the local stack.
    
    Upon cleanup, the manager deletes the local database(s) associated with this stack
    
    Usage
    -----
    
    :
        with(local_stack()) as dsc:
            context = dsc.getContext()
            # ...
    
    """

    stack = None
    try:
        (stack, userIdentity, userPassword) = __make_local_stack()
        yield stack.getAuthenticatedDataStoreCoordinator()
    finally:
        if stack is not None:
            stack.cleanUp()


class TestBase(TestCase):
    @classmethod
    def setup_class(cls):
        print("Creating local database stack...")
        (cls.local_stack, cls.dsc) = make_local_stack()


    @classmethod
    def teardown_class(cls):
        print("Removing local database stack...")
        cls.local_stack.cleanUp()

    def get_dsc(self):
        return self.__class__.dsc




