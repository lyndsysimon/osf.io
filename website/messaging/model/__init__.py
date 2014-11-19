from modularodm import fields, Q

from framework.mongo import StoredObject, ObjectId


class Channel(StoredObject):
    """A conceptual queue of messages"""
    name = fields.StringField(primary=True)

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


class Message(StoredObject):

    _id = fields.StringField(default=lambda: str(ObjectId()))
    # Message is satisfied for all channels
    #   Setting this prevents the Message from being loaded from the database
    #   for most queries.
    satisfied = False

    def satisfied_for(channel):
        """Whether or not this message is satisfied for the given channel

        :param channel Channel: The channel for which to resolve status
        :return: bool
        """
        pass

    channels = fields.ForeignField('channel', list=True, required=True)

    def __repr__(self):
        return '<Message _id="{}">'.format(self._id)