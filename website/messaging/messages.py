from modularodm import fields
from modularodm.exceptions import ValidationTypeError

from framework.mongo import StoredObject, ObjectId


def _validate_boolean_dict(item):
    """validate that dict field contains only boolean values"""
    for val in item.values():
        if not isinstance(val, bool):
            raise ValidationTypeError()


class Message(StoredObject):
    _name = 'channel'

    _id = fields.StringField(default=lambda: str(ObjectId()))

    # List of channels to which this message applies
    channels = fields.ForeignField('channel', list=True, required=True)

    # Flags - values in this dict must be booleans
    flags = fields.DictionaryField(validate=_validate_boolean_dict)

    def __repr__(self):
        return '<{name} _id="{id}">'.format(name=self.__class__.__name__,
                                            id=self._id)