import six
from modularodm import fields

from framework.mongo import StoredObject, ObjectId

from .utils import _validate_boolean_dict, InheritableStoredObject

class flag(object):
    def __init__(self, f):
        print("I've been initialized")

    def __call__(self, *args, **kwargs):
        print("I've been called")

#@six.add_metaclass(InheritableObjectMeta)
class Message(InheritableStoredObject):

    _id = fields.StringField(default=lambda: str(ObjectId()))

    # List of channels to which this message applies
    channels = fields.ForeignField('channel', list=True, required=True)

    # Flags - values in this dict must be booleans
    flags = fields.DictionaryField(validate=_validate_boolean_dict)

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self._meta = {'__class_name__': self.__class__.__name__}

    def __repr__(self):
        return '<{name} _id="{id}">'.format(name=self.__class__.__name__,
                                            id=self._id)


class AlertMessage(Message):
    """A simple alert, which may be read, unread, or archived.

    Each channel that recieves this message has a discrete "read" status."""

    @flag
    def read(self, channel):
        """Has this message been read by the channel?"""
        return False

