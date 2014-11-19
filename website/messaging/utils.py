import types

import six

from modularodm import StoredObject, Q
from modularodm.exceptions import ValidationTypeError
from modularodm.storedobject import ObjectMeta


def _validate_boolean_dict(item):
    """validate that dict field contains only boolean values"""
    for val in item.values():
        if not isinstance(val, bool):
            raise ValidationTypeError()


class InheritableObjectMeta(ObjectMeta):
    def __init__(cls, name, bases, dct):

        # # Reassign register_collection; ObjectMeta's constructor calls it
        # cls._old_register_collection = cls.register_collection
        #
        # def noop(cls):
        #     pass
        # # bind fake method to the new class
        # cls.register_collection = types.MethodType(noop, cls)

        super(InheritableObjectMeta, cls).__init__(name, bases, dct)

        # If this is the base for inheritable objects, return
        if cls.__name__ == 'InheritableStoredObject':
            return

        # Walk up the inheritance tree until we get to the direct descendant of
        #  InheritableStoredObject
        inherited_class = cls
        inherited_bases = bases
        while 'InheritableStoredObject' != inherited_bases[0].__name__:
            inherited_class = inherited_bases[0]
            inherited_bases = inherited_bases[0].__bases__


        if 'InheritableStoredObject' in [x.__name__ for x in inherited_bases]:
            cls._name = inherited_class._name


        if not hasattr(cls, '__polymorphic_type'):
            cls.__polymorphic_type = cls.__name__


        # # revert the changes so the class can be registered to a collection
        # cls.register_collection = cls._old_register_collection
        # del cls._old_register_collection


@six.add_metaclass(InheritableObjectMeta)
class InheritableStoredObject(StoredObject):

    def __init__(self, *args, **kwargs):
        pt = kwargs.get('__polymorphic_type', self._InheritableObjectMeta__polymorphic_type)
        self.__class__ = self.gather_polymorphic_types().get(pt, self)
        super(InheritableStoredObject, self).__init__(*args, **kwargs)

    @classmethod
    def find(cls, query=None, **kwargs):
        query_parts = [
            Q('__polymorphic_type', 'eq', sub._InheritableObjectMeta__polymorphic_type)
            for sub in cls.gather_subclasses()
        ]

        if query is None:
            query = query_parts.pop()

        for part in query_parts:
            query |= part

        return super(InheritableStoredObject, cls).find(query, **kwargs)

    # @classmethod
    # def from_storage(cls, data, **kwargs):
    #     pt = data.get('__polymorphic_type', cls._InheritableObjectMeta__polymorphic_type)
    #     obj_class = cls.gather_polymorphic_types().get(pt, cls)
    #     if cls is obj_class:
    #         print("Have decided on: " + repr(cls))
    #         print(repr(data))
    #         return super(InheritableStoredObject, cls).from_storage(data, **kwargs)
    #     return obj_class.from_storage(data=data, **kwargs)


    @classmethod
    def gather_subclasses(cls):
        if cls is InheritableStoredObject:
            raise RuntimeError("Cannot gather subclasses for inheritable base")
        subclasses = set()
        for sub in cls.__subclasses__():
            subclasses = subclasses | sub.gather_subclasses()
        subclasses.add(cls)
        return subclasses

    @classmethod
    def gather_polymorphic_types(cls):
        return {
            sub._InheritableObjectMeta__polymorphic_type: sub
            for sub in cls.gather_subclasses()
        }

    # @classmethod
    # def load(cls, *args, **kwargs):
    #     obj = super(InheritableStoredObject, cls).load(*args, **kwargs)
    #     data = obj._get_cached_data(obj._id)
    #     polymorphic_type = data.get('__polymorphic_type')
    #     print(polymorphic_type)
    #     resolved_class = cls.gather_polymorphic_types().get(polymorphic_type)
    #
    #     if resolved_class is None or resolved_class is cls:
    #         return obj
    #     else:
    #         return resolved_class.load(data=data)

    @classmethod
    def register_collection(cls):
        if InheritableStoredObject in cls.__bases__:
            super(InheritableStoredObject, cls).register_collection()

    def to_storage(self, *args, **kwargs):
        data = super(InheritableStoredObject, self).to_storage(*args, **kwargs)
        data['__polymorphic_type'] = self._InheritableObjectMeta__polymorphic_type
        return data