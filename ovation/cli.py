import six
import argparse

import ovation.upload as upload
import ovation.download as download


def main():
    parser = argparse.ArgumentParser(prog='python -m ovation.cli')
    subparsers = parser.add_subparsers(title='Available subcommands',
                                       description='Use `python -m ovation.cli <subcommand> -h` for additional help')

    # UPLOAD
    parser_upload = subparsers.add_parser('upload', description='Upload files to Ovation')
    parser_upload.add_argument('-u', '--user', help='Ovation user email')
    parser_upload.add_argument('parent_id', help='Project or Folder UUID')
    parser_upload.add_argument('paths', nargs='+', help='Paths to local files or directories')
    parser_upload.set_defaults(func=upload.upload_paths)
    # upload.upload_paths(user=args.user,
    #                     parent_id=args.parent_id,
    #                     paths=args.paths)


    # DOWNLOAD
    parser_download = subparsers.add_parser('download', description='Download files from Ovation')
    parser_download.add_argument('-u', '--user', help='Ovation user email')
    parser_download.add_argument('entity_id', help='File or Revision UUID')
    parser_download.add_argument('-o', '--output', help='Output directory')
    parser_download.set_defaults(func=download.download_main)
    # download.download_main(user=args.user,
    #               entity_id=args.entity_id,
    #               output=args.output)


    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
