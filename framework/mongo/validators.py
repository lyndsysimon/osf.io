from modularodm.exceptions import ValidationTypeError


def boolean_dict(item):
    """validate that dict field contains only boolean values"""
    for val in item.values():
        if not isinstance(val, bool):
            raise ValidationTypeError()