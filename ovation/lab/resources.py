import ovation.session
import ovation.download
from typing import Dict

from ovation.lab.constants import RESOURCES


def get_resource_url(session: ovation.session.Session,
                     resource_id: int) -> Dict[str, str]:
    """
    Gets the download URL for a Resource
    :param session: ovation.session.Session
    :param resource_id: resource Id
    :return: Dict of resource URL and ETag
    """

    response = session.get(session.path(RESOURCES, resource_id))
    result = {k: response[k] for k in response if k in ['url', 'etag']}

    return result
