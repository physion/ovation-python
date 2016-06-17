import mimetypes
import os.path
import threading

import boto3
import six
import argparse
import os

import ovation.core as core

from ovation.session import connect
from pprint import pprint
import pdb

def copy_bucket_contents(session, project_id, aws_access_key_id, aws_secret_access_key, source_s3_bucket, destination_s3_bucket):
    """
    Iterates through all keys in source_s3_bucket and moves it to destination_s3_bucket

    :param session: Session
    :param project_id: The id of the project where the file will be moved to
    :param directory_path: local path to directory
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    """

    src_s3_session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)

    src_s3_connection = src_s3_session.resource('s3')
    src = src_s3_connection.Bucket(source_s3_bucket)

    folder_map = {}
    parent_folder_id = project_id

    for s3_file in src.objects.all():
        is_folder = s3_file.key.endswith("/");

        if is_folder:

            # e.g key --> 'Folder1/Folder2/Folder3/'
            folder_path = s3_file.key
            folder_list = s3_file.key.split('/')
            folder_list.remove('')

            # e.g current_folder --> 'Folder3'
            current_folder = folder_list[-1]

            if len(folder_list) > 1:
                current_folder_name = current_folder + "/"
                parent_folder_path = find_parent_path(current_path=folder_path, current_entity_name=current_folder_name)
                parent_folder_id = folder_map[parent_folder_path]
                new_folder = core.create_folder(session, parent_folder_id, current_folder)

                folder_map[folder_path] = new_folder._id
            else:
                new_folder = core.create_folder(session, project_id, current_folder)
                folder_map[folder_path] = new_folder._id

        else:

            file_path = s3_file.key
            path_list = s3_file.key.split('/')

            # e.g current_file --> 'test.png'
            current_file = path_list[-1]
            parent_folder_id = project_id

            if len(path_list) > 1:
                parent_folder_path = find_parent_path(current_path=file_path, current_entity_name=current_file)
                parent_folder_id = folder_map[parent_folder_path]

            # create revision
            create_file(session=session, parent_folder_id=parent_folder_id, s3_file=s3_file, source_bucket=source_s3_bucket, destination_bucket=destination_s3_bucket, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

def find_parent_path(current_path, current_entity_name):
    """
    Takes in a fullpath ('Folder1/Folder2/Folder3/'), and a current_entity_name ('Folder3/')
    and returns the parent_path ('Folder1/Folder2/')
    """
    num_chars_to_remove = len(current_entity_name) * -1
    return current_path[:num_chars_to_remove]

def create_file(session, parent_folder_id, s3_file, source_bucket, destination_bucket, aws_access_key_id, aws_secret_access_key):
    """
    Upload a new `Revision` to `parent_file`. File is uploaded from `local_path` to
    the Ovation cloud, and the newly created `Revision` version is set.
    :param session: ovation.connection.Session
    :param parent_file: file entity dictionary or file ID string
    :param local_path: local path
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    :return: new `Revision` entity dicitonary
    """
    file_name = s3_file.key

    content_type = mimetypes.guess_type(file_name)[0]
    if content_type is None:
        content_type = 'application/octet-stream'

    new_file = core.create_file(session, parent_folder_id, file_name)

    r = session.post(new_file['links']['self'],
                     data={'entities': [{'type': 'Revision',
                                         'attributes': {'name': file_name,
                                                        'content_type': content_type}}]})
    revision = r['entities'][0]
    aws = r['aws'][0]['aws']

    aws_session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)

    s3 = aws_session.resource('s3')

    destination_file = s3.Object(destination_bucket, aws['key'])

    copy_source = "{0}/{1}".format(source_bucket, file_name)
    #client.copy_object(Bucket=destination_bucket, CopySource=copy_source, Key=file_name)

    response = destination_file.copy_from(CopySource=copy_source)

    revision['attributes']['version'] = response['VersionId']

    revision_response = session.put('/api/v1/revisions/{}'.format(revision['_id']), entity=revision)

    return revision_response

def main():
    parser = argparse.ArgumentParser(description='Transfer files from one bucket to another')

    args = parser.parse_args()


    upload_paths(user=args.user,
                 project_id=args.parent_id,
                 paths=args.paths)


if __name__ == '__main__':
    main()
