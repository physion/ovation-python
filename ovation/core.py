import six
from ovation.session import simplify_response

def create_file(session, parent, name):
    """
    Create a new `File` entity under parent.

    :param session: ovation.session.Session
    :param parent: parent Project or Folder (entity dict or ID)
    :param name: File name
    :return: created file
    """

    return _create_contents(session, 'File', parent, name)


def _create_contents(session, entity_type, parent, name):
    if isinstance(parent, six.string_types):
        parent = session.get(session.entity_path('entities', id=parent))

    result = session.post(parent.links['self'], data={'entities': [{'type': entity_type,
                                                                  'attributes': {'name': name}}]})
    return simplify_response(result['entities'][0])


def create_folder(session, parent, name):
    """
    Create a new `Folder` entity under parent.

    :param session: ovation.session.Session
    :param parent: parent Project or Folder (entity dict or ID)
    :param name: Folder name
    :return: created folder
    """

    return _create_contents(session, 'Folder', parent, name)
