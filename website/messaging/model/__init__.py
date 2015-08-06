from modularodm import fields, Q

from framework.mongo import StoredObject, ObjectId


class Channel(StoredObject):
    """A conceptual queue of messages"""
    name = fields.StringField(primary=True)

    def __iter__(self):
        for message in Message.find(Q('channels', 'eq', self)):
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