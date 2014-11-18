from nose.tools import assert_equal

from website.messaging.model import Channel, Message

from tests.base import DbTestCase


class TestMessages(DbTestCase):
    def test_message_in_channel(self):
        ch = Channel(name="MyChannel")
        ch.save()

        msg = Message()
        msg.channels = [ch, ]
        msg.save()

        assert_equal(ch, Channel.find_one())
        assert_equal(msg, Message.find_one())

        assert_equal(list(ch), [msg])
