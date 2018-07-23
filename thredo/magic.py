# magic.py

from contextlib import contextmanager
import sys

from . import socket

__all__ = ['more_magic']

@contextmanager
def more_magic():
    sockmod = sys.modules['socket']
    sys.modules['socket'] = socket
    try:
        yield
    finally:
        sys.modules['socket'] = sockmod
