import six
from ovation.session import simplify_response


FOLDER_TYPE = 'Folder'
FILE_TYPE = 'File'
REVISION_TYPE = 'Revision'
PROJECT_TYPE = 'Project'
ACTIVITY_TYPE = 'Activity'


def add_link(session, entity,
             target=None,
             rel=None,
             inverse_rel=None):
    """
    Adds a new relationship link from entity to the target. All relationships in
    Ovation are many-to-many.

    :param session: ovation.session.Session
    :param entity: relationship source entity (dict or ID)
    :param target: relationship target ID
    :param rel: relationship `rel`
    :param inverse_rel: inverse relationship (optional)
    :return: {'links': [LinkInfo],
                'entities': [Updated entities]}
    """

    if target is None:
        raise Exception("Target required")
    if rel is None:
        raise Exception("Rel required")

    entity = get_entity(session, entity)
    if (not 'relationships' in entity) or (not rel in entity['relationships']):
        raise Exception("Entity does not have a rel {}".format(rel))

    link = {'target_id': target}
    if inverse_rel:
        link['inverse_rel'] = inverse_rel

    return session.post(entity['relationships'][rel]['self'], data=[link])


def remove_link(session, entity,
                target=None,
                rel=None):

    """
    Removes relationship links from entity to the target with the given `rel`.

    :param session: ovation.session.Session
    :param entity: relationship source entity (dict or ID)
    :param target: relationship target ID
    :param rel: relationship `rel`
    """

    if target is None:
        raise Exception("Target required")
    if rel is None:
        raise Exception("Rel required")

    entity = get_entity(session, entity)
    if (not 'relationships' in entity) or (not rel in entity['relationships']):
        raise Exception("Entity does not have a rel {}".format(rel))

    relationships = session.get(entity['relationships'][rel]['self'])
    for r in relationships:
        if r['target_id'] == target:
            session.delete(session.path('relationships',
                                        entity_id=r['_id'],
                                        org=entity['organization_id']))


def create_file(session, parent, name, attributes=None):
    """
    Create a new `File` entity under parent.

    :param session: ovation.session.Session
    :param parent: parent Project or Folder (entity dict or ID)
    :param name: File name
    :param attributes: additional attributes for the file
    :return: created file
    """

    if attributes is None:
        attributes = {}

    return _create_contents(session, FILE_TYPE, parent, name, attributes=attributes)


def _create_contents(session, entity_type, parent, name, attributes=None):
    if attributes is None:
        attributes = {}

    if isinstance(parent, six.string_types):
        parent = session.get(session.path('entities', entity_id=parent))

    attributes.update({'name': name})

    attr = {'type': entity_type,
            'attributes': attributes}

    result = session.post(parent['links']['self'], data={'entities': [attr]})
    return simplify_response(result['entities'][0])


def create_folder(session, parent, name, attributes=None):
    """
    Create a new `Folder` entity under parent.

    :param session: ovation.session.Session
    :param parent: parent Project or Folder (entity dict or ID)
    :param name: Folder name
    :param attributes: additional attributes for the folder
    :return: created folder
    """

    if attributes is None:
        attributes = {}

    return _create_contents(session, FOLDER_TYPE, parent, name, attributes=attributes)


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

    return session.delete(session.path(entity_id=id))


def undelete_entity(session, entity):
    """
    Undeletes an entity

    :param session: ovation.session.Session
    :param entity: entity dict or ID
    :return: undeleted entity Dict
    """

    if isinstance(entity, six.string_types):
        entity = get_entity(session, entity, include_trash=True)

    return session.put(session.path(entity_id=entity['_id']) + "/restore", entity)


def get_entity(session, id, include_trash=False, include_annotations=False):
    """
    Gets an entity by ID

    :param session: ovation.session.Session
    :param id: entity ID
    :param: include_trash: if true, return trashed entities
    :param: include_annotations: if true, include annotations with results
    :return: entity Dict or {"entity": <entity>, "includes": [..includes..]} if include_annotations is True
    """

    if isinstance(id, six.string_types):
        params = {"trash": str(include_trash).lower()}
        if include_annotations:
            params["includes"] = "annotations"
        return session.get(session.path(entity_id=id), params=params)

    return id


def get_projects(session):
    """
    Gets all Projects visible to the authenticated user
    :param session: ovation.session.Session
    :return: list of Projects
    """
    return session.get(session.path(resource='projects'))
