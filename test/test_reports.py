from unittest.mock import patch, Mock, sentinel

from ovation.session import Session, DataDict
import ovation.lab.reports as reports


@patch('ovation.lab.upload.upload_resource')
def test_uploads_incomplete_report_resource(upload_resource):
    s = Mock(spec=Session)
    req_id = sentinel.req_id
    path = sentinel.path

    s.get.return_value = DataDict({'requisition': {'id': req_id}})

    reports.upload_incomplete_report(s,
                                     org=sentinel.org_id,
                                     requisition_id=req_id,
                                     path=path,
                                     progress=None)

    upload_resource.assert_called_with(s, req_id, path, progress=None)


@patch('ovation.lab.upload.upload_resource')
def test_creates_incomplete_report(upload_resource):
    s = Mock(spec=Session)
    req_id = sentinel.req_id
    path = sentinel.path

    s.get.return_value = DataDict({'requisition': {'id': req_id}})
    s.path.return_value = sentinel.reports_path

    upload_resource.return_value = DataDict({'id': sentinel.resource_id})

    reports.upload_incomplete_report(s,
                                     org=sentinel.org_id,
                                     requisition_id=req_id,
                                     path=path,
                                     progress=None)

    s.post.assert_called_with(sentinel.reports_path,
                              data={'report': {'organization_id': sentinel.org_id,
                                               'requisition_id': req_id,
                                               'resource_id': sentinel.resource_id}})
