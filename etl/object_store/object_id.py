"""A module containing the ObjectId class"""
from dataclasses import dataclass
from typing import Any


@dataclass
class ObjectId:
    """
    Represents an object in an object store.

    namespace -- the object store-dependent partition for objects, such as a bucket name

    path -- the POSIX-style path within the namespace of this object. Can be a directory or a file.
    """
    namespace: str
    path: str

    def __hash__(self):
        return (self.namespace + self.path).__hash__()

    def __eq__(self, other: Any):
        return self.namespace == other.namespace and \
               self.path == other.path
