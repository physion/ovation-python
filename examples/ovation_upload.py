#!/usr/bin/env python

import argparse
import os
import ovation.upload as upload

from ovation.session import connect

def main():
    parser = argparse.ArgumentParser(description='Upload files to Ovation')
    parser.add_argument('-u', '--user', help='Ovation user email')
    parser.add_argument('project_id', help='Project UUID')
    parser.add_argument('paths', nargs='+', help='Paths to local files or directories')

    args = parser.parse_args()

    upload_paths(user=args.user,
                 project_id=args.project_id,
                 paths=args.paths)


def upload_paths(user=None, project_id=None, paths=[]):
    if user is None:
        user = input('Email: ')

    if user is None:
        return

    if 'OVATION_PASSWORD' in os.environ:
        password = os.environ['OVATION_PASSWORD']
    else:
        password = None

    s = connect(user, password=password)


    for p in paths:
        print('Uploading {}'.format(p))
        if os.path.isdir(p):
            upload.upload_folder(s, project_id, p)
        else:
            upload.upload_file(s, project_id, p)


if __name__ == '__main__':
    main()
