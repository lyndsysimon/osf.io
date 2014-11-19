from modularodm import fields

from framework.mongo import StoredObject, ObjectId


class Message(StoredObject):
    _name = 'channel'

    _id = fields.StringField(default=lambda: str(ObjectId()))

    # List of channels to which this message applies
    channels = fields.ForeignField('channel', list=True, required=True)

    def __repr__(self):
        return '<Message _id="{}">'.format(self._id)