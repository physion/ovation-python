import json
import logging
import os.path

import six

import ovation.core as core
import ovation.upload as upload
import ovation.session
import requests

from tqdm import tqdm


def _resolve_links(session, project, links=[], progress=tqdm):
    resolved_links = []
    for link in progress(links,
                         leave=False,
                         unit='links'):
        if isinstance(link, six.string_types) and os.path.isfile(link):
            logging.debug("Uploading input %s", link)
            revision = upload.upload_file(session, project,
                                          link)
            resolved_links.append(revision)
        else:
            resolved_links.append(core.get_entity(session, link))

    return resolved_links


def create_activity(session, project, name, inputs=[], outputs=[], related=[], progress=tqdm):
    """
    Creates a new Activity within the given project.

    Activity inputs, outputs and related files may be specified at creation. Inputs
    may be Sources Revisions. Outputs and Related files must be Revisions. Each
    may be specified as a UUID, entity dict, or local path. For local paths, the
    local file will be uploaded to the Activity's project.

    :param session: ovation.session.Session
    :param project: Project (dict or Id)
    :param name: activity name
    :param inputs: input Revisions or Sources (dicts or Ids), or local file paths
    :param outputs: output Revisions (dicts or Ids) or local file paths
    :param related: action Revisions (dicts or Ids) or local file paths
    :return: new activity
    """
    logging.debug("Getting project")
    project = core.get_entity(session, project)

    logging.debug("Resolving inputs")
    inputs = _resolve_links(session, project, inputs, progress=progress)

    logging.debug("Resolving outputs")
    outputs = _resolve_links(session, project, outputs, progress=progress)

    logging.debug("Resolving related")
    related = _resolve_links(session, project, related, progress=progress)

    activity = {'type': core.ACTIVITY_TYPE,
                'attributes': {'name': name},
                'relationships': {'parents': {'related': [project['_id']],
                                              'type': core.PROJECT_TYPE,
                                              'inverse_rel': 'activities',
                                              'create_as_inverse': True},
                                  'inputs': {'related': [input['_id'] for input in inputs],
                                             'type': core.REVISION_TYPE,
                                             'inverse_rel': 'activities'},
                                  'outputs': {'related': [output['_id'] for output in outputs],
                                             'type': core.REVISION_TYPE,
                                             'inverse_rel': 'origins'},
                                  'actions': {'related': [r['_id'] for r in related],
                                              'type': core.REVISION_TYPE,
                                              'inverse_rel': 'procedures'}}}

    result = session.post(session.path('activities'), data={'activities': [activity]})

    return ovation.session.simplify_response(result['activities'][0])


def add_inputs(session, activity, inputs=[], progress=tqdm):
    """
    Adds inputs to an existing activity.

    Inputs may be Sources or Revisions, specified as UUIDs or entity dics. In addition,
    local files may be specified by file path. Local files will be uploaded to the
    Activity's project and the newly created Revision added as an input to
    the Activity.


    :param session: ovation.session.Session
    :param activity: activity UUID or Dict
    :param inputs: array of UUIDs, dicts, or local file paths of inputs to add
    :return:
    """
    activity = core.get_entity(session, activity)
    project = _get_project(session, activity)
    for activity_input in progress(_resolve_links(session, project, links=inputs, progress=progress),
                                   unit='inputs'):
        activity_input = core.get_entity(session, activity_input)
        core.add_link(session, activity,
                      target=activity_input['_id'],
                      rel='inputs',
                      inverse_rel='activities')


def _get_project(session, activity):
    project = core.get_entity(session, activity['links']['_collaboration_roots'][0])
    return project


def remove_inputs(session, activity, inputs=[], progress=tqdm):
    """
    Removes inputs from the given activity.

    Inputs may be Sources or Revisions, specified as UUIDs or entity dics.

    :param session: ovation.session.Session
    :param activity: activity UUID or Dict
    :param inputs: array of UUIDs or dicts
    :return:
    """
    activity = core.get_entity(session, activity)
    for activity_input in progress(inputs, unit='inputs'):
        activity_input = core.get_entity(session, activity_input)
        core.remove_link(session, activity,
                         target=activity_input['_id'],
                         rel='inputs')


def add_outputs(session, activity, outputs=[], progress=tqdm):
    """
    Adds outputs to an existing activity.

    Outputs are Revisions, specified as UUIDs or entity dics. In addition,
    local files may be specified by file path. Local files will be uploaded to the
    Activity's project and the newly created Revision added as an output to
    the Activity.


    :param session: ovation.session.Session
    :param activity: activity UUID or Dict
    :param outputs: array of UUIDs, dicts, or local file paths of outputs to add
    """
    activity = core.get_entity(session, activity)
    project = _get_project(session, activity)
    for activity_output in progress(_resolve_links(session, project, links=outputs, progress=progress),
                                    unit='outputs'):
        activity_output = core.get_entity(session, activity_output)
        core.add_link(session, activity,
                      target=activity_output['_id'],
                      rel='outputs',
                      inverse_rel='origins')


def remove_outputs(session, activity, outputs=[], progress=tqdm):
    """
    Removes outputs from the given activity.

    Outputs are Revisions, specified as UUIDs or entity dics.

    :param session: ovation.session.Session
    :param activity: activity UUID or Dict
    :param outputs: array of UUIDs or dicts
    :return:
    """
    activity = core.get_entity(session, activity)
    for activity_output in progress(outputs,
                                    unit='outputs'):
        activity_output = core.get_entity(session, activity_output)
        core.remove_link(session, activity,
                         target=activity_output['_id'],
                         rel='outputs')


def add_related(session, activity, related=[], progress=tqdm):
    """
    Adds related Revisions to an existing activity.

    Related Revisions are specified as UUIDs or entity dics. In addition,
    local files may be specified by file path. Local files will be uploaded to the
    Activity's project and the newly created Revision added as a related Revision to
    the Activity.

    :param session: ovation.session.Session
    :param activity: activity UUID or Dict
    :param related: array of Revision UUIDs or Dicts
    :return:
    """
    activity = core.get_entity(session, activity)
    project = _get_project(session, activity)
    for activity_related in progress(_resolve_links(session, project, links=related, progress=progress),
                                     unit='files'):
        activity_related = core.get_entity(session, activity_related)
        core.add_link(session, activity,
                      target=activity_related['_id'],
                      rel='actions',
                      inverse_rel='procedures')


def start_compute(session, activity, image, url, progress=tqdm):
    """
        Start the compute image from the given Activity.


        :param token: user token
        :param activity: activity UUID
        :param image: compute image
        :return:
        """
    data = {'activity_id': activity._id,
            'image_name': image,
            'organization': session.org}

    headers = {'Authorization': 'Bearer {}'.format(session.token),
               'Content-Type': 'application/json'}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    r.raise_for_status()
    return r.status_code


def remove_related(session, activity, related=[], progress=tqdm):
    """
    Removes related Revisions from the given activity.

    Related Revisions are Revisions, specified as UUIDs or entity dics.

    :param session: ovation.session.Session
    :param activity: activity UUID or Dict
    :param related: array of UUIDs or dicts
    :return:
    """
    activity = core.get_entity(session, activity)
    for activity_related in progress(related,
                                     unit='files'):
        activity_related = core.get_entity(session, activity_related)
        core.remove_link(session, activity,
                         target=activity_related['_id'],
                         rel='actions')


def create_main(args):
    session = args.session

    project_id = args.project
    if project_id is None:
        project_id = input('Project Id: ')

    name = args.name
    if name is None:
        name = input('Activity name: ')

    inputs = args.input or []
    outputs = args.output or []
    related = args.related or []

    activity = create_activity(session, project_id, name, inputs=inputs, outputs=outputs, related=related)

    if args.json:
        print(json.dumps({"activity": activity._id}))
        return

    if args.concise:
        print(activity._id)
        return

    print("Created activity: {}".format(activity._id))


def add_inputs_main(args):
    session = args.session
    activity = core.get_entity(session, args.activity_id)

    add_inputs(session, activity, args.inputs or [])

def remove_inputs_main(args):
    session = args.session
    activity = core.get_entity(session, args.activity_id)

    remove_inputs(session, activity, args.inputs or [])


def add_outputs_main(args):
    session = args.session
    activity = core.get_entity(session, args.activity_id)

    add_outputs(session, activity, args.outputs or [])

def remove_outputs_main(args):
    session = args.session
    activity = core.get_entity(session, args.activity_id)

    remove_outputs(session, activity, args.outputs or [])


def add_related_main(args):
    session = args.session
    activity = core.get_entity(session, args.activity_id)

    add_related(session, activity, args.related or [])

def remove_related_main(args):
    session = args.session
    activity = core.get_entity(session, args.activity_id)

    remove_related(session, activity, args.related or [])


def start_compute_main(args):
    session = args.session
    activity = core.get_entity(session, args.activity)
    image = args.image
    url = args.url

    start_compute(session, activity, image, url)
