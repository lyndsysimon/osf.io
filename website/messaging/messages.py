from modularodm import fields

from framework.mongo import StoredObject, ObjectId


class Message(StoredObject):
    _name = 'channel'

    _id = fields.StringField(default=lambda: str(ObjectId()))

    # List of channels to which this message applies
    channels = fields.ForeignField('channel', list=True, required=True)

    def __repr__(self):
        return '<{name} _id="{id}">'.format(name=self.__class__.__name__,
                                            id=self._id)