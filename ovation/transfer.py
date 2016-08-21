import argparse
import json
import os.path
import boto3
import logging
import csv

import functools

import ovation.core as core
import ovation.upload as upload

from ovation.session import connect
from ovation.session import Session
from tqdm import tqdm
from multiprocessing import Manager
from multiprocessing.pool import ThreadPool as Pool

# Checkpoing CSV columns
PATH = 'path'
ID = 'id'
FIELDNAMES = [PATH, ID]

# Multiprocessing pool size
POOL_SIZE = int(os.environ['TRANSFER_POOL_SIZE']) if 'TRANSFER_POOL_SIZE' in os.environ else 5


def copy_bucket_contents(session, project=None, aws_access_key_id=None, aws_secret_access_key=None,
                         source_s3_bucket=None, destination_s3_bucket=None, progress=tqdm,
                         copy_file_fn=None, checkpoint=None):
    """

    :param session:
    :param project:
    :param aws_access_key_id:
    :param aws_secret_access_key:
    :param source_s3_bucket:
    :param destination_s3_bucket:
    :param progress: show process progress (i.e. tqdm). Default: tqdm
    :return: {'folders': [ created folders ], 'files': [ copied files ] }
    """

    src_s3_session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key)

    src_s3_connection = src_s3_session.resource('s3')
    src = src_s3_connection.Bucket(source_s3_bucket)

    logging.info('Starting copy from s3 bucket: ' + str(source_s3_bucket))

    logging.info('Pool size: ' + str(POOL_SIZE))
    # Restore state from checkpoint if provided


    s3_object_list = src.objects.all()
    num_objects_to_transfer = len(list(s3_object_list))
    logging.info(str(num_objects_to_transfer) + ' objects found to transfer')

    # Go through list once for folders; tqdm
    # Go through list second time for files (multiprocessing)
    with Manager() as manager:
        entities = manager.dict()

        if checkpoint is None:
            checkpoint = '.checkpoint.csv'

        _setup_checkpoint(checkpoint, entities)

        logging.info('Creating folders')
        file_paths = []
        for s3_object in progress(s3_object_list, desc='Create folders', unit='key'):
            if s3_object.key.endswith("/"):
                # s3_object is a Folder
                # e.g. s3_object.key --> 'Folder1/Folder2/Folder3/'

                folder_path = s3_object.key
                logging.info('Listed S3 folder: ' + folder_path)

                find_or_create_folder(entities, folder_path, project, session, checkpoint)
            else:
                file_paths.append(s3_object.key)

        logging.info('Folders created')

        logging.info('Transferring files')

        session_token = session.token

        # map_args = _prepare_args(file_paths, entities, project, session_token, source_s3_bucket, destination_s3_bucket,
        #                          aws_access_key_id, aws_secret_access_key, copy_file_fn, checkpoint)

        with Pool(POOL_SIZE) as p:
            partial_find_or_create_file = functools.partial(find_or_create_file, entities, project, session_token, source_s3_bucket, destination_s3_bucket,
                                                            aws_access_key_id, aws_secret_access_key, copy_file_fn, checkpoint)

            for r in progress(p.imap_unordered(partial_find_or_create_file, file_paths), desc='Copy objects', total=len(file_paths), unit='file'):
                pass
            # p.starmap(find_or_create_file, map_args, CHUNK_SIZE)

        return dict(entities)


def _prepare_args(file_paths, entities, project, session_token, source_s3_bucket, destination_s3_bucket,
                  aws_access_key_id, aws_secret_access_key, copy_file_fn, checkpoint):
    return ([entities, file_path, project, session_token, source_s3_bucket, destination_s3_bucket,
             aws_access_key_id, aws_secret_access_key, copy_file_fn, checkpoint] for (i,file_path) in enumerate(file_paths))


def _setup_checkpoint(checkpoint, entities):
    if os.path.isfile(checkpoint):
        with open(checkpoint, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entities[row[PATH]] = row[ID]
            logging.info('Read {} entities from checkpoint file'.format(len(entities)))
    else:
        with open(checkpoint, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def find_or_create_file(entities, project, session_token, source_s3_bucket, destination_s3_bucket,
                        aws_access_key_id, aws_secret_access_key, copy_file_fn, checkpoint, file_path):
    with open(checkpoint, 'a') as checkpoint_file:
        checkpoint_writer = csv.DictWriter(checkpoint_file, fieldnames=FIELDNAMES)
        session = _make_session(session_token)

        if file_path not in entities:
            logging.info('Creating file: ' + file_path)

            path_list = file_path.split('/')

            # e.g file_name --> 'test.png'
            file_name = path_list[-1]

            if len(path_list) > 1:
                parent_folder_path = '/'.join(path_list[:-1]) + '/'
                logging.info('File parent folder is: ' + parent_folder_path)
                parent = find_or_create_folder(entities, parent_folder_path, project, session, checkpoint)
            else:
                logging.info('File parent is project')
                parent = project

            file = copy_file_fn(session, parent=parent, file_key=file_path, file_name=file_name,
                                source_bucket=source_s3_bucket, destination_bucket=destination_s3_bucket,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)

            if file is not None:
                entities[file_path] = file['_id']
                logging.info('Recording new file to checkpoing file: ' + file_path)
                checkpoint_writer.writerow({PATH: file_path, ID: file['_id']})
            else:
                logging.info('Recording copy fail to checkpoing file: ' + file_path)
                checkpoint_writer.writerow({PATH: file_path, ID: "File copy failed"})


        else:
            logging.info('No need to create file: ' + file_path + '. Found in already created files list.')


def _make_session(session_token):
    session = Session(session_token)
    return session


def find_or_create_folder(entities, folder_path, project, session, checkpoint):
    with open(checkpoint, 'a') as checkpoint_file:
        checkpoint_writer = csv.DictWriter(checkpoint_file, fieldnames=FIELDNAMES)
        folder_list = folder_path.split('/')[:-1]  # Drop trailing

        if folder_path not in entities:

            logging.info('Creating folder: ' + folder_path)

            # e.g. current_folder --> 'Folder3'
            current_folder = folder_list[-1]
            parent_folder_path = '/'.join(folder_list[:-1]) + '/'

            # if nested folder
            if len(folder_list) > 1:
                logging.info('Folder parent_folder is: ' + parent_folder_path)
                parent = find_or_create_folder(entities, parent_folder_path, project, session, checkpoint)
            else:
                logging.info('Folder parent_folder is: project')
                parent = project

            found_or_created_folder = core.create_folder(session, parent, current_folder,
                                                         attributes={'original_s3_path': folder_path})

            entities[folder_path] = found_or_created_folder['_id']

            logging.info('Recording new folder to checkpoint file: ' + folder_path)
            checkpoint_writer.writerow({PATH: folder_path, ID: found_or_created_folder['_id']})
        else:
            logging.info(folder_path + ' already in entities')
            found_or_created_folder = entities[folder_path]

        return found_or_created_folder


def copy_file(session, parent=None, file_key=None, file_name=None, source_bucket=None,
              destination_bucket=None, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Creates an Ovation 'File' and 'Revision' record.  File is transferred from
    source_bucket to destination_bucket and then the Revision` version is set to S3 version_id
    of the object in the destination_bucket.
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
    new_file = core.create_file(session, parent, file_name,
                                attributes={'original_s3_path': file_key})

    # create revision record
    r = session.post(new_file.links.self,
                     data={'entities': [{'type': 'Revision',
                                         'attributes': {'name': file_name,
                                                        'content_type': content_type}}]})

    # get key for where to copy existing file from create revision resonse
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

    try:
        aws_response = destination_file.copy_from(CopySource=copy_source)

        # get version_id from AWS copy response and update revision record with aws version_id
        # revision['attributes']['version'] = aws_response['VersionId']
        revision_response = session.put(revision['links']['upload-complete'], entity=None)

        return revision_response
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


def main():
    parser = argparse.ArgumentParser(description='Transfer files from S3 to Ovation')
    parser.add_argument('-u', '--user', help='Ovation user email')
    parser.add_argument('-p', '--password', help='Ovation password')
    parser.add_argument('-t', '--token', help='Ovation user token')
    parser.add_argument('parent', help='Project or Folder UUID that will receive transferred files')
    parser.add_argument('source_bucket', help='Source S3 Bucket')
    parser.add_argument('aws_access_key_id', help='AWS Access Key Id')
    parser.add_argument('aws_secret_access_key', help='AWS Secret Key')

    args = parser.parse_args()

    token = args.token
    if token is None:
        user = args.user
        if user is None:
            user = input('Email: ')

        session = connect(user, password=args.password)

    else:
        session = Session(token)

    aws_secret_access_key = args.aws_secret_access_key

    logging.basicConfig(level=logging.INFO, filename='ovation_transfer.log')

    copy_bucket_contents(session,
                         project=args.parent,
                         aws_access_key_id=args.aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         source_s3_bucket=args.source_bucket,
                         destination_s3_bucket='users.ovation.io',
                         checkpoint='.transfer_checkpoint.csv', copy_file_fn=copy_file)


if __name__ == '__main__':
    main()
