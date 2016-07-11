import texttable
import six

import ovation.core as core

from pprint import pprint

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


def list_contents_main(args):
    session = args.session
    parent_id = args.parent_id

    if parent_id is None or parent_id == '':

        table = texttable.Texttable()
        # table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_align(["l", "l"])
        table.add_rows([['Name', 'ID']])

        for p in core.get_projects(session):
            table.add_row([p.attributes.name, p._id])

        print(table.draw())

    else:
        contents = get_contents(session, parent_id)
        contents = contents['files'] + contents['folders']

        table = texttable.Texttable()
        table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_align(['l','l','l'])
        # table.set_cols_width([])
        table.add_rows([['Name', 'Modified', 'UUID']])
        contents.sort(key=lambda e: e.attributes.name)
        for e in contents:
            if e.type == core.FOLDER_TYPE:
                name = e.attributes.name + "/"
            else:
                name = e.attributes.name

            table.add_row([name, e.attributes['updated-at'], e._id])

        pprint(table.__dict__)
        print(table.draw())


