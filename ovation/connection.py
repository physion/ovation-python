"""
Connection utilities for the Ovation Python API
"""

from getpass import getpass

from ovation.api import Ovation
from ovation.core import Logging
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
    
    if logging:
        Logging.configureRootLoggerRollingAppender()
    
    if password is None:
        pw = getpass("Ovation password: ")
    else:
        pw = password

    updater = JarUpdater(email, password)
    updater.update_jar()
    
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


def nbgetpass(prompt="Ovation.io Credentials", passwd='passwd', email='email'):
    """getpass.getpass replacement for use in the IPython notebook.

    Presents a JQuery dialog prompting for email and password, saving each to a workspace
    variable.

    NB: you should delete the corresponding workspace variables once they are no longer needed.

    Arguments
    ---------
    prompt : string
        Dialog title
    passwd : string
        Workspace variable containing the user-entered password
    email : string
        Workspace variable containing the user-entered email
    """

    from IPython.display import display, Javascript

    display(Javascript("""
var dialog = $('<div/>').append(
    $('<input/>')
    .attr('id', 'email')
    .attr('name', 'email')
    .attr('type', 'email')
    .attr('value', '')
    ).append(
        $('<input/>')
        .attr('id', 'password')
        .attr('name', 'password')
        .attr('type', 'password')
        .attr('value', '')
    );
$(document).append(dialog);
dialog.dialog({
    resizable: false,
    modal: true,
    title: "%s",
    closeText: '',
    buttons : {
        "Okay": function () {
            IPython.notebook.kernel.execute(
                "%s = '" + $("input#password").attr('value') + "'"
            );
            IPython.notebook.kernel.execute(
                "%s = '" + $("input#email").attr('value') + "'"
            );
            $(this).dialog('close');
            dialog.remove();
        },
        "Cancel": function () {
            $(this).dialog('close');
            dialog.remove();
        }
    }
});
""" % (prompt, passwd, email)), include=['application/javascript'])
