# -*- coding: utf-8 -*-

from modularodm import FlaskStoredObject as StoredObject

from bson import ObjectId
from .handlers import client, database, set_up_storage
from .inheritable import InheritableStoredObject

__all__ = [
    'InheritableStoredObject',
    'StoredObject',
    'ObjectId',
    'client',
    'database',
    'set_up_storage',
]
