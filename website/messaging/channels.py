from modularodm import fields, Q
from modularodm.exceptions import NoResultsFound

from framework.mongo import InheritableStoredObject, ObjectId, validators

from .messages import Message


class Channel(InheritableStoredObject):
    """A conceptual queue of messages

    Iterating a Channel instance yields a generator of ``Message`` objects.

    Generally, this base class will not be instantiated directly, but will be
    subclassed to create channels with additional behaviors."""

    _id = fields.StringField(primary=True, default=lambda: str(ObjectId()))

    # A list of channels which feed directly into this channel. Additional
    #   channels may be dynamically added by subclasses.
    subchannels = fields.ForeignField('channel',
                                      list=True,
                                      default=lambda: list())

    # Keeps track of what messages have flags set for this particular channel
    #  keys: message IDs
    #  values: booleans
    _flags = fields.DictionaryField(validate=validators.boolean_dict)

    def _get_nested_names(self, names=None):
        """Compile all IDs included in a ``Channel``

        :param names: Used only for recursion - a set of ids already determined
                      to be part of this channel.
        :return: Set of IDs comprising the channel
        :rtype: set
        """
        # default to empty set
        if names is None:
            names = set()

        # handle circular references
        if self._id in names:
            return names

        # add this channel to the set
        names.add(self._id)

        # recurse for each subchannel
        for channel in self.subchannels:
            names = channel._get_nested_names(names)

        return names

    def __iter__(self):
        """Yield a sequence of ```Message``` instances"""
        # include this channel's ID
        query = Q('channels', 'eq', self._id)

        # Add all subchannel IDs to the query
        for name in self._get_nested_names():
            query |= Q('channels', 'eq', name)

        # iterate messages
        for message in Message.find(query):
            # detach the message object from the object cache
            message._clear_object_cache(key=message._id)
            message._yielded_from = self
            yield message

    def __repr__(self):
        return '<{name}: name="{id}">'.format(name=self.__class__.__name__,
                                              id=self._id)


class UserChannel(Channel):
    """Channel containing all messages for a given User"""

    # The user to which this channel belongs
    user = fields.ForeignField('user', required=True)

    @classmethod
    def for_user(cls, user):
        """Return the channel for a given user, creating it if necessary"""
        try:
            channel = cls.find_one(Q('user', 'eq', user))
        except NoResultsFound:
            channel = UserChannel(user=user)
            channel.save()

        return channel