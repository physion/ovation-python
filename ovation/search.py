__copyright__ = 'Copyright (c) 2014. Physion LLC. All rights reserved.'

import ovation

def search(data_context, query):
    """Search the Ovation database with a search query.

    Arguments
    ---------

    data_context : us.physion.ovation.DataContext
        Database context that will run the search

    query : string
        Query string. See http://docs.ovation.io/ for more information about the query syntax.

    Returns
    -------
    entities : iterable of us.physion.ovation.domain.OvationEntity
        Iterable of all entities in the database that match the query.
    """

    return data_context.query(ovation.autoclass('us.physion.ovation.domain.OvationEntity'), query).get()
