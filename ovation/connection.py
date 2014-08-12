"""
Connection utilities for the Ovation Python API
"""

from getpass import getpass
from ovation.jar import JarUpdater


def connect(email, password=None, logging=True):
    """Creates a new authenticated DataStoreCoordinator.
    
    Arguments
    ---------
    email : string
        Ovation.io account email
    
    password : string, optional
        Ovation.io account passowrd. If ommited, the password will be prompted at the command prompt
        
    logging : boolean, optional
        If true, configures Ovation logging. Logs will be placed in the default application
        support directory, `~/Library/Application Support/us.physion.ovation/logs` on OS X, etc.
    
    Returns
    -------
    dsc : ovation.DataStoreCoordinator
        A new authenticated DataStoreCoordinator
    
    """

    if password is None:
        pw = getpass("Ovation password: ")
    else:
        pw = password

    updater = JarUpdater(email, pw)
    updater.update_jar()


    from ovation.api import Ovation
    from ovation.core import Logging
    
    if logging:
        Logging.configureRootLoggerRollingAppender()

    print("Ovation API v{}".format(Ovation.getVersion()))
    return Ovation.connect(email, pw)


def new_data_context(email, password=None, logging=True):
    """Creates a new authenticated DataContext.
    
    Arguments
    ---------
    email : string
        Ovation.io account email
    
    password : string, optional
        Ovation.io account passowrd. If ommited, the password will be prompted at the command prompt
        
    logging : boolean, optional
        If true, configures Ovation logging. Logs will be placed in the default application
        support directory, `~/Library/Application Support/us.physion.ovation/logs` on OS X, etc.
    
    Returns
    -------
    context : ovation.DataContext
        A new authenticated DataContext
    
    """
    
    return connect(email, password=password, logging=logging).getContext()



