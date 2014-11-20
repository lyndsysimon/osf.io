from nose.tools import assert_raises

from modularodm.exceptions import ValidationTypeError

from framework.mongo import validators

from tests.base import DbTestCase


class TestValidators(DbTestCase):
    def test_validate_boolean_dict(self):
        # Shouldn't raise an exception
        validators.boolean_dict({'a': True, 'b': False})

        with assert_raises(ValidationTypeError):
            validators.boolean_dict({'a': 1})
