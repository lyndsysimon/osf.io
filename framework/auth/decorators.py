# -*- coding: utf-8 -*-

import functools

from flask import request

from framework import status
from framework.flask import redirect
from .core import Auth


def collect_auth(func):

    @functools.wraps(func)
    def wrapped(*args, **kwargs):

        kwargs['auth'] = Auth.from_kwargs(request.args.to_dict(), kwargs)
        return func(*args, **kwargs)

    return wrapped

def must_be_logged_in(*args, **kwargs):
    """
    NOTE TO FUTURE SELF: This doesn't work on redirects for non-logged-in users,
    because those users don't have a session established.

    :param args:
    :param kwargs:
    :return:
    """
    if len(args) == 1 and callable(args[0]):
        return _must_be_logged_in(args[0])
    else:
        message = kwargs.get("message")
        message_kind = kwargs.get("message_kind")
        return lambda func: _must_be_logged_in(func,
                                               message=message,
                                               message_kind=message_kind)


def _must_be_logged_in(func, message=None, message_kind=None):
    """Require that user be logged in. Modifies kwargs to include the current
    user.

    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        kwargs['auth'] = Auth.from_kwargs(request.args.to_dict(), kwargs)
        if kwargs['auth'].logged_in:
            return func(*args, **kwargs)
        else:

            if message:
                status.push_status_message(message, message_kind)

            return redirect('/login/?next={0}'.format(request.path))

    return wrapped
