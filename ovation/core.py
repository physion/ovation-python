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


def delete_entity(session, entity):
    """
    Deletes an entity. Deleted entities are put in the "trash" and are no longer visible
    or returned by GET operations. Trashed entities can be restored from the trash by
    calling `undelete_entity`.

    :param session: ovation.session.Session
    :param entity: entity dict or ID
    :return: deleted entity Dict
    """

    try:
        id = entity['_id']
    except TypeError:
        id = entity

    return session.delete(session.entity_path(id=id))


def undelete_entities(session, entity):
    """
    Undeletes an entity

    :param session: ovation.session.Session
    :param entity: entity dict or ID
    :return: undeleted entity Dict
    """

    if isinstance(entity, six.string_types):
        entity = get_entity(session, entity, include_trash=True)

    del entity['trash_info']

    return session.put(session, entity)


def get_entity(session, id, include_trash=False):
    """
    Gets an entity by ID

    :param session: ovation.session.Session
    :param id: entity ID
    :param: include_trash: if true, return trashed entities
    :return: entity Dict
    """

    return session.get(session.entity_path(id=id), params={"include-trashed": include_trash})
