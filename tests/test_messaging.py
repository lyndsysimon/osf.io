from nose.tools import assert_equal, assert_is_not_none, assert_raises

from modularodm.exceptions import ValidationTypeError

from website.messaging.messages import Message, AlertMessage
from website.messaging.channels import Channel, UserChannel
from tests.base import DbTestCase
from tests.factories import UserFactory
from website.messaging.utils import _validate_boolean_dict


class TestUtilities(DbTestCase):
    def test_validate_boolean_dict(self):
        # Shouldn't raise an exception
        _validate_boolean_dict({'a': True, 'b': False})

        with assert_raises(ValidationTypeError):
            _validate_boolean_dict({'a': 1})

class TestChannels(DbTestCase):
    def test_message_in_channel(self):
        ch = Channel(name="MyChannel")
        ch.save()

        msg = Message(channels=[ch, ])
        msg.save()

        assert_equal(ch, Channel.find_one())
        assert_equal(msg, Message.find_one())

        assert_equal([msg], list(ch))


class TestNestedChannels(DbTestCase):
    def setUp(self):
        super(TestNestedChannels, self).setUp()
        self.grandchild = Channel(name="Bottom")
        self.grandchild.save()
        self.child = Channel(name="Middle", subchannels=[self.grandchild])
        self.child.save()
        self.parent = Channel(name="Top", subchannels=[self.child])
        self.parent.save()

    def test_nested_names(self):
        assert_equal(
            self.grandchild._get_nested_names(),
            {self.grandchild._id}
        )
        assert_equal(
            self.child._get_nested_names(),
            {self.child._id, self.grandchild._id}
        )
        assert_equal(
            self.parent._get_nested_names(),
            {self.parent._id, self.child._id, self.grandchild._id}
        )

    def test_messages(self):
        top_message = Message(channels=[self.parent])
        top_message.save()
        middle_message = Message(channels=[self.child])
        middle_message.save()
        bottom_message = Message(channels=[self.grandchild])
        bottom_message.save()

        assert_equal([bottom_message], list(self.grandchild))
        assert_equal([middle_message, bottom_message], list(self.child))
        assert_equal([top_message, middle_message, bottom_message], list(self.parent))

    def test_circular_nesting(self):
        self.grandchild.subchannels.append(self.parent)
        self.grandchild.save()

        assert_equal(self.grandchild.subchannels, [self.parent._id])

        all_three = {self.parent._id, self.child._id, self.grandchild._id}

        assert_equal(self.parent._get_nested_names(), all_three)
        assert_equal(self.child._get_nested_names(), all_three)
        assert_equal(self.grandchild._get_nested_names(), all_three)


class TestUserChannel(DbTestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_from_user_not_created(self):
        channel = UserChannel.for_user(self.user)

        assert_equal(channel.user, self.user)
        assert_is_not_none(channel._id)