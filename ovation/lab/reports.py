import tqdm

import ovation.lab.upload as upload


def upload_incomplete_report(session, org=None, requisition_id=None, path=None, progress=tqdm.tqdm):
    if requisition_id is None:
        raise Exception("Requisition ID required")
    if path is None:
        raise Exception("Local report path required")
    if org is None:
        raise Exception("Organization required")

    req = session.get(session.path('requisition', requisition_id, include_org=False))

    resource = upload.upload_resource(session, req['requisition']['id'], path, progress=progress)

    return session.post(session.path('reports'), data={'report': {'organization_id': org,
                                                                  'requisition_id': requisition_id,
                                                                  'resource_id': resource.id}})
