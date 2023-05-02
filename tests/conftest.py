import contextlib

from docchain.settings import conf


@contextlib.contextmanager
def override_settings(**overrides):
    settings = conf
    original = {}
    try:
        for key, value in overrides.items():
            original[key] = getattr(settings, key)
            setattr(settings, key, value)

        yield
    finally:
        for key, value in original.items():
            setattr(settings, key, value)
