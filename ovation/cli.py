import os

import six
import argparse

import ovation.upload as upload
import ovation.download as download
import ovation.contents as contents
import ovation.session as session


def main():
    parser = argparse.ArgumentParser(prog='python -m ovation.cli')
    parser.add_argument('-u', '--user', help='Ovation user email')

    subparsers = parser.add_subparsers(title='Available subcommands',
                                       description='Use `python -m ovation.cli <subcommand> -h` for additional help')

    # UPLOAD
    parser_upload = subparsers.add_parser('upload', description='Upload files to Ovation')
    parser_upload.add_argument('parent_id', help='Project or Folder UUID')
    parser_upload.add_argument('paths', nargs='+', help='Paths to local files or directories')
    parser_upload.set_defaults(func=upload.upload_paths)
    # upload.upload_paths(user=args.user,
    #                     parent_id=args.parent_id,
    #                     paths=args.paths)


    # DOWNLOAD
    parser_download = subparsers.add_parser('download', description='Download files from Ovation')
    parser_download.add_argument('entity_id', help='File or Revision UUID')
    parser_download.add_argument('-o', '--output', help='Output directory')
    parser_download.set_defaults(func=download.download_main)


    # CONTENTS
    parser_ls = subparsers.add_parser('list',
                                      aliases=['ls'],
                                      description='List Projects or Contents')

    parser_ls.add_argument('parent_id', nargs='?', help='(Optional) Project or Folder ID', default='')

    parser_ls.set_defaults(func=contents.list_contents_main)

    args = parser.parse_args()

    if args.user is None:
        args.user = input('Email: ')

    if 'OVATION_PASSWORD' in os.environ:
        password = os.environ['OVATION_PASSWORD']
    else:
        password = None

    s = session.connect(args.user, password=password)
    args.session = s

    args.func(args)


if __name__ == '__main__':
    main()
