import boto3
import argparse

import ovation.core as core
import ovation.upload as upload

from ovation.session import connect


def copy_bucket_contents(session, project_id, aws_access_key_id, aws_secret_access_key, source_s3_bucket,
                         destination_s3_bucket):
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

    for s3_object in src.objects.all():

        # e.g. s3_object.key --> 'Folder1/Folder2/Folder3/'
        is_folder = s3_object.key.endswith("/")

        if is_folder:

            folder_path = s3_object.key
            folder_list = s3_object.key.split('/')
            folder_list.remove('')

            # e.g. current_folder --> 'Folder3'
            current_folder = folder_list[-1]

            # if nested folder
            if len(folder_list) > 1:
                current_folder_name = current_folder + "/"
                parent_folder_path = find_parent_path(current_path=folder_path, current_entity_name=current_folder_name)
                parent_folder_id = folder_map[parent_folder_path]
                new_folder = core.create_folder(session, parent_folder_id, current_folder)

                folder_map[folder_path] = new_folder._id
            else:
                # folder is at project root (project_id is the parent_id)
                new_folder = core.create_folder(session, project_id, current_folder)
                folder_map[folder_path] = new_folder._id

        else:
            # s3_object is a file
            file_path = s3_object.key
            path_list = s3_object.key.split('/')

            # e.g file_name --> 'test.png'
            file_name = path_list[-1]
            parent_folder_id = project_id

            if len(path_list) > 1:
                parent_folder_path = find_parent_path(current_path=file_path, current_entity_name=file_name)
                parent_folder_id = folder_map[parent_folder_path]

            # create revision
            copy_file(session=session, file_key=file_path, file_name=file_name, parent_folder_id=parent_folder_id,
                      source_bucket=source_s3_bucket, destination_bucket=destination_s3_bucket,
                      aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


def find_parent_path(current_path, current_entity_name):
    """
    Takes in a fullpath ('Folder1/Folder2/Folder3/'), and a current_entity_name ('Folder3/')
    and returns the parent_path ('Folder1/Folder2/')
    """
    num_chars_to_remove = len(current_entity_name) * -1
    return current_path[:num_chars_to_remove]


def copy_file(session, parent_folder_id=None, file_key=None, file_name=None, source_bucket=None,
              destination_bucket=None, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Creates an Ovation 'File' and 'Revision' record.   a new `Revision` to `parent_file`. File is uploaded from `local_path` to
    the Ovation cloud, and the newly created `Revision` version is set.
    :param session: ovation.connection.Session
    :param parent_folder_id:
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
    new_file = core.create_file(session, parent_folder_id, file_name)

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
    ovation_user_email = input('Ovation email: ')
    session = connect(ovation_user_email)

    source_s3_bucket = input('Source S3 bucket: ')
    aws_access_key_id = input('AWS Key ID: ')
    aws_secret_access_key = input('AWS Secret Key: ')

    project_id = input('Destination Ovation project id: ')
    destination_s3_bucket = 'users.ovation.io'

    copy_bucket_contents(session, project_id=project_id, aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key, source_s3_bucket=source_s3_bucket,
                         destination_s3_bucket=destination_s3_bucket)


if __name__ == '__main__':
    main()
