# sync.py
#
# The basic synchronization primitives such as locks, semaphores, and condition variables.

__all__ = [ 'Event', 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition' ]

import curio

# -- Thredo
from .thr import TAWAIT as AWAIT

class Event(object):
    def __init__(self):
        self._evt = curio.Event()

    def is_set(self):
        return self._evt.is_set()

    def clear(self):
        self._evt.clear()

    def wait(self):
        AWAIT(self._evt.wait)

    def set(self):
        AWAIT(self._evt.set)

# Base class for all synchronization primitives that operate as context managers.

class _LockBase(object):
    def __enter__(self):
        self._lock.__enter__()

    def __exit__(self, *args):
        self._lock.__exit__(*args)

    def acquire(self):
        AWAIT(self._lock.acquire)

    def release(self):
        AWAIT(self._lock.release)

    def locked(self):
        return self._lock.locked()

class Lock(_LockBase):
    def __init__(self):
        self._lock = curio.Lock()

class RLock(_LockBase):
    def __init__(self):
        self._lock = curio.RLock()

class Semaphore(_LockBase):
    def __init__(self):
        self._lock = curio.Semaphore()

    @property
    def value(self):
        return self._lock.value

class BoundedSemaphore(Semaphore):
    def __init__(self):
        self._lock = curio.BoundedSemaphore()

class Condition(_LockBase):
    def __init__(self, lock=None):
        if lock is None:
            self._lock = curio.Condition(curio.Lock())
        else:
            self._lock = curio.Condition(lock._lock)

    def locked(self):
        return self._lock.locked()

    def wait(self):
        AWAIT(self._lock.wait)
    
    def wait_for(self, predicate):
        AWAIT(self._lock.wait_for, predicate)

    def notify(self, n=1):
        AWAIT(self._lock.notify, n)

    def notify_all(self):
        AWAIT(self._lock.notify_all)

