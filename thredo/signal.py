# signal.py
#
# Signal related functionality

__all__ = ['SignalEvent']

# -- Standard Library
from curio.thread import TAWAIT as AWAIT

class SignalEvent:
    def __init__(self, *args, **kwargs):
        async def _run():
            self._sigevt = curio.SignalEvent(*args, **kwargs)
        AWAIT(_run)

    def __del__(self):
        async def _run():
            del self._sigevt
        AWAIT(_run)

    def wait(self):
        AWAIT(self._sigevt.wait)

    def set(self):
        AWAIT(self._sigevt.set)

