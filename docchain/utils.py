def set_nested_val(obj: dict, path: str, value: any):
    *path, last = path.split(".")

    for key in path:
        if not isinstance(obj, dict):
            raise TypeError(f"Cannot set key {key} on non-dict object {obj}")

        obj = obj.setdefault(key, {})

    obj[last] = value
