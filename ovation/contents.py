import functools
import texttable

import ovation.core as core

from pprint import pprint
from tqdm import tqdm
from multiprocessing.pool import ThreadPool as Pool

import pdb
"""
Walks through the directory from the specified parent yields a 3-tuple of parent entity,
folders in parent entity and files in parent entity.
If recurse is set to true, then this function will continue through all sub-folders, otherwise
it will yeild only the contents of the specified parent.
:param session: ovation.session.Session
:param parent: Project or Folder dict or ID
:yields: 4-tuple of 'parent', 'folders', 'files', and head_revisions
"""
def walk(session, parent, recurse=False):

    folders = []
    files = []
    revisions = []

    entries = get_contents(session, parent)

    for file in entries['files']:
        files.append(file)
        revision = _get_head_revision(session, file)
        revisions.append(revision)

    for folder in entries['folders']:
        folders.append(folder)

    # Yield
    yield parent, folders, files, revisions

    # Recurse into sub-directories
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

def _get_head_revision(session, file):
    headRevisions = session.get(file.links.heads)
    if(headRevisions):
        return headRevisions[0]
    else:
        return None


def _get_head(session, file):
    return {'file': file._id,
            'revision': session.get(file.links.heads)[0]._id}


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
        files = contents['files']
        folders = contents['folders']

        # revisions = {}
        # with Pool() as pool:
        #     for r in tqdm(pool.imap_unordered(functools.partial(_get_head, session), files),
        #                   desc='Finding HEAD revisions',
        #                   unit=' file',
        #                   total=len(files)):
        #         revisions[r['file']] = r['revision']


        table = texttable.Texttable()
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
