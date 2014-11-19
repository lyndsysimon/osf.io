from modularodm import fields, Q
from modularodm.exceptions import NoResultsFound

from framework.mongo import ObjectId, StoredObject

from .messages import Message


class Channel(StoredObject):
    """A conceptual queue of messages"""
    name = fields.StringField(primary=True, default=lambda: str(ObjectId()))

    subchannels = fields.ForeignField('channel',
                                      list=True,
                                      default=lambda: list())

    def _get_nested_names(self, names=None):
        # default to empty set
        if names is None:
            names = set()

        # handle circular references
        if self.name in names:
            return names

        names.add(self.name)

        # recurse for each subchannel
        for channel in self.subchannels:
            names = channel._get_nested_names(names)

        return names

    def __iter__(self):
        query = Q('channels', 'eq', self.name)

        for name in self._get_nested_names():
            query |= Q('channels', 'eq', name)

        for message in Message.find(query):
            yield message

    def __repr__(self):
        return '<Channel: name="{}">'.format(self.name)


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