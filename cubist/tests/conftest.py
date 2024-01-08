from contextlib import contextmanager


@contextmanager
def no_raise():
    yield
