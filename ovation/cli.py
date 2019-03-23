import os

import six
import argparse

import ovation.upload as upload
import ovation.download as download
import ovation.contents as contents
import ovation.session as session
import ovation.activities as activities


def main():
    parser = argparse.ArgumentParser(prog='python -m ovation.cli')
    parser.add_argument('-u', '--user', help='Ovation user email')
    parser.add_argument('-o', '--organization', help='Organization Id', default=0)
    parser.add_argument('-t', '--token', help='Ovation API token', default=None)
    parser.add_argument('--development', help='Use development environment', default=False, action='store_true')

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

    # ACTIVITIES
    activities_create = subparsers.add_parser('create-activity', description='Create a new Activity')
    activities_create.add_argument('-n', '--name', help='New activity name', required=True)
    activities_create.add_argument('-p', '--project', help='Project UUID')
    activities_create.add_argument('--json', action='store_true', help="Output Activity ID as JSON", default=False)
    activities_create.add_argument('--concise', help='Output Activity ID suitable for assignment to a shell variable', action='store_true', default=False)
    activities_create.add_argument('--input', action='append', help='Input Source or Revision UUIDs')
    activities_create.add_argument('--output', action='append', help='Outpur Revision UUIDs')
    activities_create.add_argument('--related', action='append', help='Related Revision UUIDs')
    activities_create.set_defaults(func=activities.create_main)

    activities_add_inputs = subparsers.add_parser('add-inputs', description='Add inputs to an activity')
    activities_add_inputs.add_argument('activity_id', help='Activity UUID')
    activities_add_inputs.add_argument('inputs', nargs='+', help='Input Source or Revision UUIDs')
    activities_add_inputs.set_defaults(func=activities.add_inputs_main)

    activities_remove_inputs = subparsers.add_parser('remove-inputs', description='Remove inputs to an activity')
    activities_remove_inputs.add_argument('activity_id', help='Activity UUID')
    activities_remove_inputs.add_argument('inputs', nargs='+', help='Input Source or Revision UUIDs')
    activities_remove_inputs.set_defaults(func=activities.remove_inputs_main)

    activities_add_outputs = subparsers.add_parser('add-outputs', description='Add outputs from an activity')
    activities_add_outputs.add_argument('activity_id', help='Activity UUID')
    activities_add_outputs.add_argument('outputs', nargs='+', help='Output Revision UUIDs')
    activities_add_outputs.set_defaults(func=activities.add_outputs_main)

    activities_remove_outputs = subparsers.add_parser('remove-outputs', description='Remove outputs from an activity')
    activities_remove_outputs.add_argument('activity_id', help='Activity UUID')
    activities_remove_outputs.add_argument('outputs', nargs='+', help='Output Revision UUIDs')
    activities_remove_outputs.set_defaults(func=activities.remove_outputs_main)

    activities_add_related = subparsers.add_parser('add-related', description='Add files related to an activity')
    activities_add_related.add_argument('activity_id', help='Activity UUID')
    activities_add_related.add_argument('related', nargs='+', help='Related Revision UUIDs')
    activities_add_related.set_defaults(func=activities.add_related_main)

    activities_remove_related = subparsers.add_parser('remove-related', description='Remove files related to an activity')
    activities_remove_related.add_argument('activity_id', help='Activity UUID')
    activities_remove_related.add_argument('related', nargs='+', help='Related Revision UUIDs')
    activities_remove_related.set_defaults(func=activities.remove_related_main)

    activities_start_compute = subparsers.add_parser('hpc-run', description='Start the compute to an activity')
    activities_start_compute.add_argument('--activity', help='Activity UUID', required=True)
    activities_start_compute.add_argument('--image', help='The name of the image to compute', required=True)
    activities_start_compute.add_argument('--url', help='The url of hpc-manager', default='https://hpc.ovation.io/hpc_run')
    activities_start_compute.set_defaults(func=activities.start_compute_main)

    args = parser.parse_args()

    if not 'func' in args is None:
        parser.print_help()
        return 1

    if args.user is None and args.token is None:
        args.user = input('Email: ')

    if args.development:
        api = session.DEVELOPMENT_HOST
    else:
        api = session.DEFAULT_HOST

    args.session = session.connect(args.user, token=args.token, api=api, org=args.organization)

    return args.func(args)


if __name__ == '__main__':
    result = main()
    exit(result if result is not None else 0)
