# pylint: skip-file
from etl.object_store.object_id import ObjectId

NAMESPACE = "test_namespace"

def test_ObjectId():
    PATH = "/path/to/file"

    obj = ObjectId(NAMESPACE, PATH)
    assert NAMESPACE == obj.namespace
    assert PATH == obj.path

    assert obj in {
        obj: True
    }

    assert not ObjectId('nope', 'nope') in {
        obj: True
    }

    assert obj == ObjectId(NAMESPACE, PATH)
    assert obj != ObjectId(NAMESPACE, 'nope')
    assert obj != ObjectId('nope', PATH)
