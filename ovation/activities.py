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

    result = session.post(project['links']['self'], data={'entities': [activity]})

    return ovation.session.simplify_response(result['entities'][0])


def add_inputs(session, activity, inputs=[]):
    activity = core.get_entity(session, activity)
    for activity_input in inputs:
        activity_input = core.get_entity(session, activity_input)
        core.add_link(session, activity,
                      target=activity_input['_id'],
                      rel='inputs',
                      inverse_rel='activities')


def remove_inputs(session, activity, inputs=[]):
    pass


def add_outputs(session, activity, outputs=[]):
    activity = core.get_entity(session, activity)
    for activity_output in outputs:
        activity_output = core.get_entity(session, activity_output)
        core.add_link(session, activity,
                      target=activity_output['_id'],
                      rel='outputs',
                      inverse_rel='origins')


def remove_outputs(session, activity, outputs=[]):
    pass
