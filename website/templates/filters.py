import functools


class disables_default_filters(object):
    """Decorator for Mako filters, disables default filters for a Mako context
    """
    def __init__(self, func):
        self._func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def __eq__(self, value):
        """Returns `True` if compared to the string 'n' or the wrapped object

        Internally, Mako checks the list of filters for the presence of the 'n'
        filter. This signals that the default filters for the context should not
        be applied. Since it's using a simple membership test
        (`"n" in filters`), this ensures that if the wrapped filter is in the
        list, this test will pass.
        """
        if value == 'n':
            return True
        return self._func == value
