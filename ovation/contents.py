import texttable
import logging

import ovation.core as core

create_file = core.create_file
create_folder = core.create_folder

def walk(session, parent, recurse=False):
    """
    Walks through the directory from the specified parent, yielding a 5-tuple of 'parent', 'folders',
    'files'.

    If recurse is set to true, then this function will continue through all sub-folders, otherwise
    it will yield only the contents of the specified parent.

    You can get the breadcrumb path of parent with `get_breadcrumbs`. You can get the HEAD revisions of file(s) with
    `get_head_revisions`. This example shows how to calculate the total byte size of all head revisions in a directory
    tree::

    total_bytes = 0
    for (parent, folders, files) in contents.walk(session, parent):
        for f in files:
            rev = contents.get_head_revision(session, f)
            total_bytes += rev.attributes.get('content_length', 0)

    print("Total bytes: {}".format(total_bytes))

    :param session: ovation.session.Session
    :param parent: Project or Folder dict or ID
    :returns generator of 5-tuple: `(parent, folders, files)`
    """

    folders = []
    files = []

    # if specified parent param is only a string id, will get entity object,
    # otherwise will use passed in parent param
    parent = core.get_entity(session, parent)

    entries = get_contents(session, parent)

    for file in entries['files']:
        files.append(file)

    for folder in entries['folders']:
        folders.append(folder)

    # yield
    yield parent, folders, files

    # recurse into sub-directories
    if recurse:
        for folder in folders:
            yield from walk(session, folder, recurse)


def get_contents(session, parent):
    """
    Gets all files and folders of parent
    :param session: ovation.session.Session
    :param parent: Project or Folder dict or ID
    :return: Dict of 'files' and 'folders'
    """

    p = core.get_entity(session, parent)

    if p is None:
        return None

    return {'files': session.get(p.relationships.files.related),
            'folders': session.get(p.relationships.folders.related)}


def get_head_revision(session, file):
    """
    Retrieves the head revision of file specified
    :param session: ovation.session.Session
    :param file: File dict or ID
    :return: Revision dict or None if there are no head revisions
    """

    file = core.get_entity(session, file)

    headRevisions = session.get(file.links.heads)
    if (headRevisions):
        return headRevisions[0]
    else:
        logging.warning("No head revisions found for file " + file.attributes.name)
        return None


def get_breadcrumbs(session, entity):
    """
    Returns the directory path of the entity (folder or file specified)
    :param session: ovation.session.Session
    :param entity: File / Folder dict or ID
    :return: string representing directory path of specified entity (e.g. "project1/folder1/file1.txt")
    """

    entity_directory_path = ""

    entity = core.get_entity(session, entity)

    if not entity.type in [core.FILE_TYPE, core.FOLDER_TYPE]:
        raise ValueError("entity is not a File or Folder")

    breadcrumb_list = session.get(session.path(resource="breadcrumbs"), params={"id": entity['_id']})

    if (breadcrumb_list):

        # service returns an array of multiple breadcrumbs
        # since parents (i.e folders or projects) can only have one breadcrumb, take the first and only one returned
        first_breadcrumb = breadcrumb_list[0]

        # to print out the path, reverse the list since it puts the project last
        first_breadcrumb.reverse()

        for crumb in first_breadcrumb:
            entity_directory_path += crumb['name']
            if (crumb['type'] == "Folder" or crumb['type'] == "Project"):
                entity_directory_path += "/"

    return entity_directory_path


def _get_head(session, file):
    return {'file': file._id,
            'revision': session.get(file.links.heads)[0]._id}


def list_contents_main(args):
    session = args.session
    parent_id = args.parent_id

    if parent_id is None or parent_id == '':

        table = texttable.Texttable(max_width=0)
        # table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_align(["l", "l"])
        table.add_rows([['Name', 'ID']])

        for p in core.get_projects(session):
            table.add_row([p.attributes.name, p._id])

        print(table.draw())

    else:
        contents = get_contents(session, parent_id)
        files = contents['files']
        folders = contents['folders']

        table = texttable.Texttable(max_width=0)
        table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_align(['l', 'l', 'l'])
        # table.set_cols_width([])
        table.add_rows([['Name', 'Modified', 'ID']])
        for e in sorted(files + folders, key=lambda e: e.attributes.name):
            if e.type == core.FOLDER_TYPE:
                name = e.attributes.name + "/"
                # head = ''
            else:
                name = e.attributes.name
                # head = revisions[e._id]

            table.add_row([name, e.attributes['updated-at'], e._id])

        print(table.draw())
