import functools
import texttable

import ovation.core as core

from pprint import pprint
from tqdm import tqdm
from multiprocessing.pool import ThreadPool as Pool


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
