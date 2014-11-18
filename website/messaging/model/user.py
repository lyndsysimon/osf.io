from . import Channel


class UserChannel(Channel):
    """Channel containing all messages for a given User"""

    def __init__(self, *args, **kwargs):
        return super(UserChannel, self).__init__(*args, **kwargs)

    @classmethod
    def from_user(cls, user):
        return cls(name="guid:{}".format(user._id))
