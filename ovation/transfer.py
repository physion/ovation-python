import argparse
import json
import os.path
from getpass import getpass

import boto3

import ovation.core as core
import ovation.upload as upload

from ovation.session import connect
from tqdm import tqdm


def copy_bucket_contents(session, project=None, aws_access_key_id=None, aws_secret_access_key=None,
                         source_s3_bucket=None, destination_s3_bucket=None, progress=tqdm,
                         copy_file=None, checkpoint=None):

    """

    :param session:
    :param project:
    :param aws_access_key_id:
    :param aws_secret_access_key:
    :param source_s3_bucket:
    :param destination_s3_bucket:
    :aram progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    :return: {'folders': [ created folders ], 'files': [ copied files ] }
    """

    src_s3_session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key)

    src_s3_connection = src_s3_session.resource('s3')
    src = src_s3_connection.Bucket(source_s3_bucket)

    folder_map = {}
    files = {}

    if checkpoint is not None:
        if os.path.isfile(checkpoint):
            with open(checkpoint,'r') as f:
                r = json.load(f)
                folder_map = r['folder_map']
                files = r['files']

    for s3_object in src.objects.all():

        if checkpoint is not None:
            with open(checkpoint, 'w') as f:
                json.dump({'files': files, 'folder_map': folder_map}, f)

        if s3_object.key.endswith("/"):
            # s3_object is a Folder
            # e.g. s3_object.key --> 'Folder1/Folder2/Folder3/'

            folder_path = s3_object.key
            folder_list = folder_path.split('/')[:-1]  # Drop trailing

            # e.g. current_folder --> 'Folder3'
            current_folder = folder_list[-1]
            parent_folder_path = '/'.join(folder_list[:-1]) + '/'

            # if nested folder
            if len(folder_list) > 1:
                parent = folder_map[parent_folder_path]
                new_folder = core.create_folder(session, parent, current_folder)

                folder_map[folder_path] = new_folder
            else:
                # folder is at project root (project_id is the parent_id)
                new_folder = core.create_folder(session, project, current_folder)
                folder_map[folder_path] = new_folder

        else:
            # s3_object is a file
            file_path = s3_object.key
            path_list = s3_object.key.split('/')

            # e.g file_name --> 'test.png'
            file_name = path_list[-1]
            parent = project

            if len(path_list) > 1:
                parent = folder_map[parent_folder_path]

            # create revision
            if file_path not in files:
                files[file_path] = copy_file(session, file_key=file_path, file_name=file_name, parent=parent,
                                             source_bucket=source_s3_bucket, destination_bucket=destination_s3_bucket,
                                             aws_access_key_id=aws_access_key_id,
                                             aws_secret_access_key=aws_secret_access_key)

    return {'files': files.values(), 'folders': folder_map.values()}


def find_parent_path(current_path, current_entity_name):
    """
    Takes in a fullpath ('Folder1/Folder2/Folder3/'), and a current_entity_name ('Folder3/')
    and returns the parent_path ('Folder1/Folder2/')
    """
    num_chars_to_remove = len(current_entity_name) * -1
    return current_path[:num_chars_to_remove]


def copy_file(session, parent=None, file_key=None, file_name=None, source_bucket=None,
              destination_bucket=None, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Creates an Ovation 'File' and 'Revision' record.   a new `Revision` to `parent_file`. File is uploaded from `local_path` to
    the Ovation cloud, and the newly created `Revision` version is set.
    :param session: ovation.connection.Session
    :param parent: Project or Folder (entity dict or ID)
    :param file_key: S3 Key of file to copy from source bucket
    :param file_name: Name of file
    :param source_bucket: the S3 bucket to copy file from
    :param destination_bucket: the destination_bucket to copy file to
    :param aws_access_key_id: id for key that must have read access to source and write access to destination
    :param aws_secret_access_key: AWS key
    :return: new `Revision` entity dicitonary
    """

    content_type = upload.guess_content_type(file_name)

    # create file record
    new_file = core.create_file(session, parent, file_name)

    # create revision record
    r = session.post(new_file.links.self,
                     data={'entities': [{'type': 'Revision',
                                         'attributes': {'name': file_name,
                                                        'content_type': content_type}}]})

    # get key for where to copy exisitng file from create revision resonse
    revision = r['entities'][0]
    destination_s3_key = r['aws'][0]['aws']['key']

    # Copy file from source bucket to destination location
    # Need to use key that has 'list' and 'get_object' privleges on source bucket as well as 'write' privleges
    # on destination bucket (can't use the temp aws key from the create revision response since this does
    # not have read access to the source bucket)
    aws_session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)

    s3 = aws_session.resource('s3')
    destination_file = s3.Object(destination_bucket, destination_s3_key)
    copy_source = "{0}/{1}".format(source_bucket, file_key)
    aws_response = destination_file.copy_from(CopySource=copy_source)

    # get version_id from AWS copy response and update revision record with aws version_id
    revision['attributes']['version'] = aws_response['VersionId']
    revision_response = session.put(revision['links']['self'], entity=revision)

    return revision_response


def main():
    parser = argparse.ArgumentParser(description='Transfer files from S3 to Ovation')
    parser.add_argument('-u', '--user', help='Ovation user email')
    parser.add_argument('parent', help='Project or Folder UUID that will receive transferred files')
    parser.add_argument('source_bucket', help='Source S3 Bucket')
    parser.add_argument('aws_access_key_id', help='AWS Access Key Id')
    parser.add_argument('-p', '--password', help='Ovation password')

    args = parser.parse_args()

    user = args.user
    if user is None:
        user = input('Email: ')

    session = connect(user, password=args.password)

    aws_secret_access_key = getpass("AWS Secret Access Key: ")

    copy_bucket_contents(session,
                         project=args.parent,
                         aws_access_key_id=args.aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         source_s3_bucket=args.source_bucket,
                         destination_s3_bucket='users.ovation.io')


if __name__ == '__main__':
    main()
