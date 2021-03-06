# -*- coding: utf-8 -*-

import furl
from modularodm import Q
from rest_framework.reverse import reverse
from api.base.exceptions import Gone
from rest_framework.exceptions import NotFound
from modularodm.exceptions import NoResultsFound

from website import util as website_util  # noqa
from website import settings as website_settings


def absolute_reverse(view_name, query_kwargs=None, args=None, kwargs=None):
    """Like django's `reverse`, except returns an absolute URL. Also add query parameters."""
    relative_url = reverse(view_name, kwargs=kwargs)

    url = website_util.api_v2_url(relative_url, params=query_kwargs)
    return url


def get_object_or_error(model_cls, query_or_pk, display_name=None):
    display_name = display_name or None

    if isinstance(query_or_pk, basestring):
        query = Q('_id', 'eq', query_or_pk)
    else:
        query = query_or_pk

    try:
        obj = model_cls.find_one(query)
        if getattr(obj, 'is_deleted', False) is True:
            if display_name is None:
                raise Gone
            else:
                raise Gone(detail='The requested {name} is no longer available.'.format(name=display_name))
        if hasattr(obj, 'is_active'):
            if not getattr(obj, 'is_active', False):
                if display_name is None:
                    raise Gone
                else:
                    raise Gone(detail='The requested {name} is no longer available.'.format(name=display_name))
        return obj

    except NoResultsFound:
        raise NotFound

def waterbutler_url_for(request_type, provider, path, node_id, token, obj_args=None, **query):
    """Reverse URL lookup for WaterButler routes
    :param str request_type: data or metadata
    :param str provider: The name of the requested provider
    :param str path: The path of the requested file or folder
    :param str node_id: The id of the node being accessed
    :param str token: The cookie to be used or None
    :param dict **query: Addition query parameters to be appended
    """
    url = furl.furl(website_settings.WATERBUTLER_URL)
    url.path.segments.append(request_type)

    url.args.update({
        'path': path,
        'nid': node_id,
        'provider': provider,
    })

    if token is not None:
        url.args['cookie'] = token

    if 'view_only' in obj_args:
        url.args['view_only'] = obj_args['view_only']

    url.args.update(query)
    return url.url
