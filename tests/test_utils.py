import pytest
from docchain.utils import set_nested_val


@pytest.mark.parametrize(
    "obj, path, res",
    [
        ({}, "a", {"a": 1}),
        ({}, "a.b", {"a": {"b": 1}}),
        ({}, "a.b.c", {"a": {"b": {"c": 1}}}),
        ({"a": {"_": "_"}}, "a.b.c", {"a": {"_": "_", "b": {"c": 1}}}),
    ],
)
def test_set_nested_key(obj: dict, path: str, res):
    set_nested_val(obj=obj, path=path, value=1)
    assert obj == res


@pytest.mark.parametrize(
    "obj, path, err_mess",
    [
        ({"a": 1}, "a.b.c", "Cannot set key b on non-dict object 1"),
        (
            {"a": {"b": None}},
            "a.b.c",
            "'NoneType' object does not support item assignment",
        ),
    ],
)
def test_set_nested_key__type_errors(obj: dict, path: str, err_mess: str):
    with pytest.raises(TypeError) as exc_info:
        set_nested_val(obj=obj, path=path, value=1)
    assert exc_info.value.args[0] == err_mess
