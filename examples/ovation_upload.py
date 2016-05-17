#!/usr/bin/env python

import argparse
import os

from ovation.session import connect
from ovation.upload import upload_revision

def main():
    parser = argparse.ArgumentParser(description='Upload files to Ovation')
    parser.add_argument('-u', '--user', help='Ovation user email')
    parser.add_argument('project_id', help='Project UUID')
    parser.add_argument('paths', nargs='+', help='Path to local files or directories')

    args = parser.parse_args()

    upload_files(user=args.user,
                 project_id=args.project_id,
                 paths=args.paths)


def upload_files(user=None, project_id=None, paths=[]):
    if user is None:
        user = input('Email: ')

    if user is None:
        return

    if 'OVATION_PASSWORD' in os.environ:
        password = os.environ['OVATION_PASSWORD']
    else:
        password = None

    s = connect(user, password=password)
    project = s.get(s.make_type_path('entities', id=project_id))
    project_url = project.links.self

    for p in paths:
        name = os.path.basename(p)
        f = s.post(project_url, data={'entities': [{'type': 'File',
                                                    'attributes': {'name': name}}]})

        print('\tUploading {}'.format(p))
        upload_revision(s, f, p)


if __name__ == '__main__':
    main()
