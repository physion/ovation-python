import logging
import os.path

import six

import ovation.core as core
import ovation.upload as upload
import ovation.session


def _resolve_links(session, project, links=[]):
    resolved_links = []
    for link in links:
        if isinstance(link, six.string_types) and os.path.isfile(link):
            logging.debug("Uploading input %s", link)
            revision = upload.upload_file(session, project,
                                          link)
            resolved_links.append(revision)
        else:
            resolved_links.append(core.get_entity(session, link))

    return resolved_links


def create_activity(session, project, name, inputs=[], outputs=[], related=[]):
    """
    Creates a new Activity.

    :param session: ovation.session.Session
    :param project: Project (dict or Id)
    :param name: activity name
    :param inputs: input Revisions or Sources (dicts or Ids), or local file paths
    :param outputs: output Revisions (dicts or Ids) or local file paths
    :param related:
    :return:
    """
    logging.debug("Getting project")
    project = core.get_entity(session, project)

    logging.debug("Resolving inputs")
    inputs = _resolve_links(session, project, inputs)

    logging.debug("Resolving outputs")
    outputs = _resolve_links(session, project, outputs)

    logging.debug("Resolving related")
    related = _resolve_links(session, project, related)

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


def add_inputs(session, activity, inputs=[]):
    activity = core.get_entity(session, activity)
    project = _get_project(session, activity)
    for activity_input in _resolve_links(session, project, links=inputs):
        activity_input = core.get_entity(session, activity_input)
        core.add_link(session, activity,
                      target=activity_input['_id'],
                      rel='inputs',
                      inverse_rel='activities')


def _get_project(session, activity):
    project = core.get_entity(session, activity['links']['_collaboration_roots'][0])
    return project


def remove_inputs(session, activity, inputs=[]):
    activity = core.get_entity(session, activity)
    for activity_input in inputs:
        activity_input = core.get_entity(session, activity_input)
        core.remove_link(session, activity,
                         target=activity_input['_id'],
                         rel='inputs')


def add_outputs(session, activity, outputs=[]):
    activity = core.get_entity(session, activity)
    project = _get_project(session, activity)
    for activity_output in _resolve_links(session, project, links=outputs):
        activity_output = core.get_entity(session, activity_output)
        core.add_link(session, activity,
                      target=activity_output['_id'],
                      rel='outputs',
                      inverse_rel='origins')


def remove_outputs(session, activity, outputs=[]):
    activity = core.get_entity(session, activity)
    for activity_output in outputs:
        activity_output = core.get_entity(session, activity_output)
        core.remove_link(session, activity,
                         target=activity_output['_id'],
                         rel='outputs')


def add_related(session, activity, related=[]):
    activity = core.get_entity(session, activity)
    project = _get_project(session, activity)
    for activity_related in _resolve_links(session, project, links=related):
        activity_related = core.get_entity(session, activity_related)
        core.add_link(session, activity,
                      target=activity_related['_id'],
                      rel='actions',
                      inverse_rel='procedures')


def remove_related(session, activity, related=[]):
    activity = core.get_entity(session, activity)
    for activity_related in related:
        activity_related = core.get_entity(session, activity_related)
        core.remove_link(session, activity,
                         target=activity_related['_id'],
                         rel='actions')
